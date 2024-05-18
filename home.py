from flask import Flask, render_template, redirect, url_for, request, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import csv

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Обеспечьте безопасность вашего приложения, используя секретный ключ

# Файл для хранения данных пользователей
USER_DATA_FILE = 'users.csv'


# Функция для чтения данных из CSV-файла
def read_user_data():
    user_data = {}
    with open(USER_DATA_FILE, 'r') as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            username, password, balance = row
            user_data[username] = {'password': password, 'balance': float(balance)}
    return user_data


# Функция для записи данных в CSV-файл
def write_user_data(user_data):
    with open(USER_DATA_FILE, 'w', newline='') as file:
        csv_writer = csv.writer(file)
        for username, data in user_data.items():
            csv_writer.writerow([username, data['password'], data['balance']])


@app.route('/')
def index():
    # Проверьте, вошел ли пользователь в систему
    if 'username' in session:
        username = session['username']
        user_data = read_user_data()
        balance = user_data.get(username, {}).get('balance', 0)
        return render_template('home.html', username=username, balance=balance)
    else:
        return render_template('home.html')


@app.route('/roulette')
def roulette():
    return redirect('http://localhost:2000')


@app.route('/rock-paper-scissors')
def rock_paper_scissors():
    return redirect('http://localhost:3000')


@app.route('/dice')
def dice():
    return redirect('http://localhost:4000')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user_data = read_user_data()
        if username in user_data and check_password_hash(user_data[username]['password'], password):
            # Успешная авторизация
            session['username'] = username
            return redirect(url_for('index'))
        else:
            flash('Неправильный логин или пароль')

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Проверяем, существует ли уже пользователь с таким именем
        user_data = read_user_data()
        if username in user_data:
            flash('Пользователь с таким именем уже существует')
            return redirect(url_for('register'))

        # Хэшируем пароль перед сохранением
        hashed_password = generate_password_hash(password)

        # Добавляем нового пользователя в данные
        user_data[username] = {'password': hashed_password, 'balance': 0}

        # Записываем данные в CSV-файл
        write_user_data(user_data)

        # После успешной регистрации пользователь сразу входит в систему
        session['username'] = username
        return redirect(url_for('index'))

    return render_template('register.html')


@app.route('/logout')
def logout():
    # Удалить пользователя из сессии
    session.pop('username', None)
    return redirect(url_for('index'))


@app.route('/deposit', methods=['GET', 'POST'])
def deposit():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    user_data = read_user_data()

    if request.method == 'POST':
        amount = float(request.form.get('amount'))
        if amount > 0:
            # Пополнить баланс пользователя
            user_data[username]['balance'] += amount
            write_user_data(user_data)
            flash('Баланс успешно пополнен')

    balance = user_data[username]['balance']
    return render_template('deposit.html', username=username, balance=balance)


if __name__ == '__main__':
    app.run(port=1000)
