import sqlite3

class FDataBase:
    def __init__(self, db):
        self.__db = db
        self.__cur = db.cursor()

    def getMenu(self):
        sql = '''SELECT * FROM mainmenu'''
        try:
            self.__cur.execute(sql)
            res = self.__cur.fetchall()
            if res: return res
        except:
            print("Ошибка чтения из БД")
        return []

    def addUser(self, login, hpsw):
        try:
            self.__cur.execute(f"SELECT COUNT() as 'count' FROM users WHERE login LIKE '{login}'")
            res = self.__cur.fetchone()
            if res['count'] > 0:
                print("Пользователь с таким login уже существует")
                return False

            self.__cur.execute("INSERT INTO users (login, psw) VALUES (?, ?)", (login, hpsw))
            self.__db.commit()

        except sqlite3.Error as e:
            print("Ошибка добавления пользователя в БД "+str(e))
            return False

        return True

    def changeRights(self, login, imp, exp, lab):
        try:
            self.__cur.execute(f"SELECT COUNT() as 'count' FROM users WHERE login LIKE '{login}'")
            res = self.__cur.fetchone()
            if res['count'] == 0:
                print("Пользователь с таким login не существует")
                return False

            self.__cur.execute(f"UPDATE users SET import=?, export=?, labeling=? WHERE login LIKE '{login}'", (imp,exp,lab))
            self.__db.commit()

        except sqlite3.Error as e:
            print("Ошибка изменения прав в БД "+str(e))
            return False

        return True   

    def getUser(self, user_id):
        try:
            self.__cur.execute(f"SELECT * FROM users WHERE id = {user_id} LIMIT 1")
            res = self.__cur.fetchone()
            if not res:
                print("Пользователь не найден")
                return False

            return res
        except sqlite3.Error as e:
            print("Ошибка получения данных из БД "+str(e))

        return False

    def getUserByLogin(self, login):
        try:
            self.__cur.execute(f"SELECT * FROM users WHERE login = '{login}' LIMIT 1")
            res = self.__cur.fetchone()
            if not res:
                print("Пользователь не найден")
                return False

            return res
        except sqlite3.Error as e:
            print("Ошибка получения данных из БД "+str(e))

        return False
