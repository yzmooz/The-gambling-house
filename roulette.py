from flask import Flask, request, jsonify, render_template, session
from config import secret_key
import random
import requests

app = Flask(__name__)
app.secret_key = secret_key

MAIN_SERVER_URL = 'http://localhost:1000'

# Инициализация глобальных переменных
previous_win_number = 0
current_win_number = 0


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

    if 'big_wins' not in session:
        session['big_wins'] = []
    if 'bet_history' not in session:
        session['bet_history'] = []

    return render_template('roulette.html',
                           balance=balance, big_wins=session['big_wins'], bet_history=session['bet_history'])


@app.route('/bet', methods=['POST'])
def place_bet():
    global previous_win_number, current_win_number

    bets = request.form.get('bets')
    if not bets:
        return jsonify({'result': 'error', 'message': 'Отсутствуют ставки'})

    bets = eval(bets)  # Преобразуем строку JSON в словарь

    balance = get_user_balance()
    if balance is None:
        return jsonify({'result': 'error', 'message': 'Ошибка авторизации. Пожалуйста, войдите на основном сайте.'})

    total_bet_amount = sum(bets.values())
    if total_bet_amount > balance:
        return jsonify({'result': 'error', 'message': 'Недостаточно средств на балансе'})

    total_win = 0
    win_number = random.randint(0, 36)

    for bet, amount in bets.items():
        win = check_bet(win_number, bet, amount)
        total_win += win
        balance -= amount  # Списываем ставку со счета

    previous_win_number = current_win_number
    current_win_number = win_number

    balance += total_win  # Добавляем выигрыш к балансу
    update_user_balance(balance)

    rotation_angle = calculate_angle(current_win_number)

    session['bet_history'].insert(0, {'bets': ", ".join(bets.keys()), 'amount': total_bet_amount, 'win': total_win})
    if len(session['bet_history']) > 10:
        session['bet_history'].pop()

    if total_win > 5000:
        session['big_wins'].insert(0, f'Выигрыш {total_win}$ (Ставки: {", ".join(bets.keys())})')
        if len(session['big_wins']) > 10:
            session['big_wins'].pop()

    return jsonify({
        'result': 'success',
        'win': total_win,
        'balance': balance,
        'bet_history': session['bet_history'],
        'big_wins': session['big_wins'],
        'current_win_number': current_win_number,
        'previous_win_number': previous_win_number,
        'rotation_angle': rotation_angle
    })


def calculate_angle(num2):
    numbers = [
        0, 32, 15, 19, 4, 21, 2, 25, 17, 34, 6, 27, 13, 36, 11,
        30, 8, 23, 10, 5, 24, 16, 33, 1, 20, 14, 31, 9, 22, 18,
        29, 7, 28, 12, 35, 3, 26
    ]
    sector_size = 360 / len(numbers)

    index_diff = numbers.index(num2)
    angle = index_diff * sector_size
    if angle <= 0:
        angle += 360

    return angle + 360


def check_bet(win_number, bet, amount):
    win_numbers = {
        'RED': [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36],
        'BLACK': [2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35],
        'GREEN': [0]
    }

    if bet in win_numbers and win_number in win_numbers[bet]:
        multiplier = 2 if bet in ['RED', 'BLACK'] else 35
        win_amount = multiplier * amount
        return win_amount
    elif bet.isdigit() and int(bet) == win_number:
        multiplier = 35
        win_amount = multiplier * amount
        return win_amount
    elif bet == "1st 12" and 1 <= win_number <= 12:
        multiplier = 3
        win_amount = multiplier * amount
        return win_amount
    elif bet == "2nd 12" and 13 <= win_number <= 24:
        multiplier = 3
        win_amount = multiplier * amount
        return win_amount
    elif bet == "3rd 12" and 25 <= win_number <= 36:
        multiplier = 3
        win_amount = multiplier * amount
        return win_amount
    elif bet == "1-18" and 1 <= win_number <= 18:
        multiplier = 2
        win_amount = multiplier * amount
        return win_amount
    elif bet == "19-36" and 19 <= win_number <= 36:
        multiplier = 2
        win_amount = multiplier * amount
        return win_amount
    elif bet == "EVEN" and win_number % 2 == 0 and win_number != 0:
        multiplier = 2
        win_amount = multiplier * amount
        return win_amount
    elif bet == "ODD" and win_number % 2 != 0:
        multiplier = 2
        win_amount = multiplier * amount
        return win_amount
    else:
        return 0


if __name__ == '__main__':
    app.run(port=2000)
