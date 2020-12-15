import sqlite3
from flask import Blueprint, render_template, request, url_for, redirect, flash, session, g


admin = Blueprint('admin', __name__, template_folder='templates', static_folder='static')

menu = [{'url': '.index', 'title': 'Панель'},
        {'url': '.listusers', 'title': 'Список пользователей'},
        {'url': '.rights', 'title': 'Редактировать права'},
        {'url': '.logout', 'title': 'Выйти'}]

def login_admin():
    session['admin_logged'] = 1

def isLogged():
    return True if session.get('admin_logged') else False

def logout_admin():
    session.pop('admin_logged', None)

db = None

@admin.before_request
def before_request():
    """Установление соединения с БД перед выполнением запроса"""
    global db
    db = g.get('link_db')

@admin.teardown_request
def teardown_request(request):
    global db
    db = None
    return request

@admin.route('/')
def index():
    if not isLogged():
        return redirect(url_for('.login'))

    return render_template('index.html', menu=menu, title='Админ-панель')

@admin.route('/login', methods=["POST", "GET"])
def login():
    if isLogged():
        return redirect(url_for('.index'))

    if request.method == "POST":
        if request.form['user'] == 'admin' and request.form['psw'] == '12345':
            login_admin()
            return redirect(url_for('.index'))
        else:
            flash("Неверная пара логин/пароль", "error")

    return render_template('login.html', title='Админ-панель')

@admin.route('/logout', methods=["POST", "GET"])
def logout():
    if not isLogged():
        return redirect(url_for('.login'))
    
    logout_admin()

    return redirect(url_for('.login'))

@admin.route('/list-users')
def listusers():
    if not isLogged():
        return redirect(url_for('.login'))

    list = []
    if db:
        try:
            cur = db.cursor()
            cur.execute(f"SELECT login, import, export, labeling FROM users ORDER BY id")
            list = cur.fetchall()
        except sqlite3.Error as e:
            print("Ошибка получения пользователей из БД " + str(e))

    return render_template('listusers.html', title='Список пользователей', menu=menu, list=list)

@admin.route('/rights', methods=["POST", "GET"])
def rights():
    if not isLogged():
        return redirect(url_for('.login'))

    if request.method == "POST":
        if ('login' in request.form) and ('imp' in request.form) and ('exp' in request.form) and ('lab' in request.form):
            login = request.form['login']
            imp = request.form['imp']
            exp = request.form['exp']
            lab = request.form['lab']

            if db:
                try:
                    cur = db.cursor()
                    cur.execute(f"UPDATE users SET import=?, export=?, labeling=? WHERE login LIKE '{login}'", (imp,exp,lab))
                    db.commit()
                    flash("Права успешно установлены", "success")
                except sqlite3.Error as e:
                    print("Ошибка изменения БД " + str(e))
                    flash("Ошибка изменения БД", "error")
        else:
            flash("Неверно заполнены поля", "error")
  
  
    return render_template('rights.html', title='Изменение прав', menu=menu)