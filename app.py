from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.secret_key = "supersecretkey" #для сессий куки и безопасности

login_manager = LoginManager()
login_manager.init_app(app) #подключает фласк логин
login_manager.login_view = "login" #если не авторизован перекидывает на логин
login_manager.login_message = "Пожалуйста, войдите для доступа к этой странице"

# Пользователь
class User(UserMixin):
    def __init__(self, id):
        self.id = id

# база данных
users = {
    "user": {"password": "qwerty","visits": 0}}


@login_manager.user_loader #загрузка пользователя вызывает при каждом запросе
def load_user(user_id):
    if user_id in users:
        return User(user_id)
    return None


# Главная
@app.route("/")
def index():
    return render_template("index.html")


# Счетчик посещений 
@app.route("/counter")
def counter():
    if current_user.is_authenticated:
        # авторизованный пользователь
        username = current_user.id
        users[username]["visits"] += 1
        visits = users[username]["visits"]

    else:
        # гость (через session)
        if "visits" in session:
            session["visits"] += 1
        else:
            session["visits"] = 1

        visits = session["visits"]

    return render_template("counter.html", visits=visits)


# ===== Логин =====
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST": #Получение данных
        username = request.form["username"]
        password = request.form["password"]
        remember = True if request.form.get("remember") else False
#Проверка
        if username in users and users[username]["password"] == password:
            user = User(username)
            login_user(user, remember=remember) #успещный вход сохраняет в сессии
#если пытался зайти на сикрет без авторизации перекидывает на логин
            next_page = request.args.get("next")
            flash("Успешный вход!", "success")
            return redirect(next_page or url_for("index"))
        else:
            flash("Неверный логин или пароль", "danger")

    return render_template("login.html")


# выход
@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Вы вышли из системы", "info")
    return redirect(url_for("index"))


# Секретная страница
@app.route("/secret")
@login_required #не авторизован
def secret():#если авторизован
    return render_template("secret.html")


if __name__ == "__main__":
    app.run(debug=True, port=5001)