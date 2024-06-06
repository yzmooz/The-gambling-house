from flask import Flask, request, jsonify, render_template, session
from config import secret_key
import random
import requests

MAIN_SERVER_URL = 'http://localhost:1000'

app = Flask(__name__)
app.secret_key = secret_key


def get_user_balance():
    response = requests.get(f'{MAIN_SERVER_URL}/api/get_balance', cookies=request.cookies)
    if response.status_code == 200:
        return response.json().get('balance', 0)
    return None


def update_user_balance(new_balance):
    response = requests.post(f'{MAIN_SERVER_URL}/api/update_balance',
                             json={'balance': new_balance}, cookies=request.cookies)
    return response.status_code == 200


@app.route('/')
def index():
    balance = get_user_balance()
    if balance is None:
        return "Ошибка авторизации. Пожалуйста, войдите на основном сайте.", 401
    if 'bet_history' not in session:
        session['bet_history'] = []

    return render_template('dice.html', balance=balance, bet_history=session['bet_history'])


@app.route('/bet', methods=['POST'])
def place_bet():
    bet = request.form.get('bet', type=float)
    chance = request.form.get('chance', type=float)
    balance = get_user_balance()

    if balance is None:
        return jsonify({'result': 'error', 'message': 'Ошибка авторизации. Пожалуйста, войдите на основном сайте.'})

    if bet > balance:
        return jsonify({'result': 'error', 'message': 'Недостаточно средств на балансе'})
    if bet <= 0 or chance <= 0 or chance >= 100:
        return jsonify({'result': 'error', 'message': 'Некорректные данные ставки'})

    coefficient = (100 - chance) / chance
    outcome = random.randint(0, 100)

    if outcome < chance:
        win_amount = bet * coefficient
        balance += win_amount
        result = {'message': f'Вы выиграли! Выпавшее число: {outcome:.2f}', 'win': True, 'outcome': outcome}
    else:
        balance -= bet
        result = {'message': f'Вы проиграли! Выпавшее число: {outcome:.2f}', 'win': False, 'outcome': outcome}

    update_success = update_user_balance(balance)
    if not update_success:
        return jsonify({'result': 'error', 'message': 'Не удалось обновить баланс на сервере'})

    session['bet_history'].insert(0, {'bet': bet, 'chance': chance, 'win': result['win'], 'message': result['message']})
    if len(session['bet_history']) > 10:
        session['bet_history'].pop()

    result.update({'balance': balance, 'bet_history': session['bet_history']})
    return jsonify(result)


if __name__ == '__main__':
    app.run(port=4000)
