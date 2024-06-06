from flask import Flask, render_template, request, jsonify, session
from datetime import datetime, timedelta
from config import secret_key
import random
import requests

app = Flask(__name__)
app.secret_key = secret_key

MAIN_SERVER_URL = 'http://localhost:1000'


def get_user_balance():
    if 'balance' in session and 'balance_timestamp' in session:
        if datetime.now() - session['balance_timestamp'] < timedelta(seconds=10):
            return session['balance']

    response = requests.get(f'{MAIN_SERVER_URL}/api/get_balance', cookies=request.cookies)
    if response.status_code == 200:
        session['balance'] = response.json().get('balance', 0)
        session['balance_timestamp'] = datetime.now()
        return session['balance']
    return None


def update_user_balance(new_balance):
    response = requests.post(f'{MAIN_SERVER_URL}/api/update_balance', json={'balance': new_balance}, cookies=request.cookies)
    if response.status_code == 200:
        session['balance'] = new_balance
        session['balance_timestamp'] = datetime.now()
        return True
    return False


@app.route('/')
def index():
    balance = get_user_balance()
    if balance is None:
        return "Ошибка авторизации. Пожалуйста, войдите на основном сайте.", 401
    return render_template('rps.html', balance=balance)


@app.route('/play', methods=['POST'])
def play():
    balance = get_user_balance()
    if balance is None:
        return jsonify({'error': 'Ошибка авторизации. Пожалуйста, войдите на основном сайте.', 'balance': 0})

    player_choice = request.form['player_choice']
    bet_amount = int(request.form['bet_amount'])

    if bet_amount > balance:
        response = {
            'error': 'Недостаточно средств для ставки.',
            'balance': balance
        }
        return jsonify(response)

    choices = ['rock', 'paper', 'scissors']
    computer_choice = random.choice(choices)

    if player_choice == computer_choice:
        result = "It's a tie!"
        result_class = "tie"
        amount = 0
    elif (player_choice == 'rock' and computer_choice == 'scissors') or \
            (player_choice == 'paper' and computer_choice == 'rock') or \
            (player_choice == 'scissors' and computer_choice == 'paper'):
        result = "You win!"
        result_class = "win"
        amount = bet_amount
        balance += bet_amount
    else:
        result = "Computer wins!"
        result_class = "loss"
        amount = -bet_amount
        balance -= bet_amount

    if not update_user_balance(balance):
        return jsonify({'error': 'Не удалось обновить баланс на сервере', 'balance': balance})

    response = {
        'result': result,
        'computer_choice': computer_choice,
        'balance': balance,
        'result_class': result_class,
        'amount': amount
    }
    return jsonify(response)


if __name__ == '__main__':
    app.run(port=3000)
