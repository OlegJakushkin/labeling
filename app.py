import json
from types import SimpleNamespace
from flask import Flask, make_response, g, render_template, request, flash, redirect, url_for
from label_studio.blueprint import (blueprint as label_studio_blueprint,
                                    LabelStudioConfig, set_external_hostname, project_get_or_create)
import sqlite3
import os
from FDataBase import FDataBase
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from UserLogin import UserLogin

from admin.admin import admin


app = Flask('my-ml-platform',  static_url_path='')
app = Flask(__name__)
app.secret_key = 'some-secret-key'
app.config['WTF_CSRF_ENABLED'] = False
app.url_map.strict_slashes = False  # it's very important to disable this option
app.register_blueprint(label_studio_blueprint, url_prefix='/label-studio/')
app.register_blueprint(admin, url_prefix='/admin')

# check label_studio.utils.argparser to know all options: *_parser.add_argument(option_name, ...)
input_args = {'project_name': 'my_project', 'command': 'start', 'root_dir': '.', 'force': False}
set_external_hostname('http://localhost:5000/label-studio')
app.label_studio = LabelStudioConfig(input_args=SimpleNamespace(**input_args))

menu = [{"name": 'Регистрация', "url": 'register'},
        {"name": 'Label Studio', "url": 'label-studio'}]

# ==================================== DATABASE ==================================================

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Авторизуйтесь для доступа к закрытым страницам'
login_manager.login_message_category = 'success'

@login_manager.user_loader
def load_user(user_id):
    print("load_user")
    return UserLogin().fromDB(user_id, dbase)

app.config.update(dict(DATABASE=os.path.join(app.root_path, 'labeling.db')))

def connect_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

def create_db():
    db = connect_db()
    with app.open_resource('sq_db.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    db.close()


def get_db():
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()
    return g.link_db

dbase = None
@app.before_request
def before_request():
    global dbase
    db = get_db()
    dbase = FDataBase(db)

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'link_db'):
        g.link_db.close()

# ==================================== APP ================================================

@app.route("/")
def index():
    return render_template('_index.html', title='Labeling Service', menu=dbase.getMenu())

@app.route("/login", methods=["POST", "GET"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('profile'))

    if request.method == "POST":
        user = dbase.getUserByLogin(request.form['login'])
        if user and check_password_hash(user['psw'], request.form['psw']):
            userlogin = UserLogin().create(user)
            rm = True if request.form.get('remainme') else False
            login_user(userlogin, remember=rm)
            return redirect(request.args.get('next') or url_for('profile'))

        flash("Неверная пара логин/пароль", "error")

    return render_template('_login.html', title='Авторизация', menu=dbase.getMenu())

@app.route("/register", methods=["POST","GET"])
def register():
    if request.method == "POST":
        if len(request.form['login']) > 4 and len(request.form['psw']) > 4 and request.form['psw'] == request.form['psw2']:
            hash = generate_password_hash(request.form['psw'])
            res = dbase.addUser(request.form['login'], hash)
            if res:
                flash("Вы успешно зарегистрированы", "success")
                return redirect(url_for('login'))
            else:
                flash("Ошибка при добавлении в БД", "error")
        else:
            flash("Неверно заполнены поля", "error")
  
    return render_template('_register.html', title='Регистрация', menu=dbase.getMenu())


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Вы вышли из аккаунта", "success")
    return redirect(url_for('login'))

@app.route('/profile')
@login_required
def profile():
    return render_template("_profile.html", menu=dbase.getMenu(), title="Профиль")


if __name__ == '__main__':
    app.run(debug=True)