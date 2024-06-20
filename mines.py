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


def initialize_board(num_mines):
    board = [['' for _ in range(5)] for _ in range(5)]
    mines_placed = 0
    while mines_placed < num_mines:
        row = random.randint(0, 4)
        col = random.randint(0, 4)
        if board[row][col] != 'M':
            board[row][col] = 'M'
            mines_placed += 1
    return board


@app.route('/')
def index():
    balance = get_user_balance()
    if balance is None:
        return "Ошибка авторизации. Пожалуйста, войдите на основном сайте.", 401
    if 'history' not in session:
        session['history'] = []

    return render_template('mines.html', balance=balance, history=session['history'],
                           current_multiplier=1.00, board=[['']*5 for _ in range(5)])


@app.route('/play', methods=['POST'])
def play():
    bet = request.form.get('bet', type=float)
    num_mines = request.form.get('num_mines', type=int)
    balance = get_user_balance()

    if balance is None:
        return jsonify({'success': False, 'message': 'Ошибка авторизации. Пожалуйста, войдите на основном сайте.'})

    if bet > balance:
        return jsonify({'success': False, 'message': 'Недостаточно средств на балансе'})
    if bet <= 0 or num_mines < 2 or num_mines > 24:
        return jsonify({'success': False, 'message': 'Некорректные данные ставки'})

    board = initialize_board(num_mines)
    balance -= bet
    update_success = update_user_balance(balance)
    if not update_success:
        return jsonify({'success': False, 'message': 'Не удалось обновить баланс на сервере'})

    session['board'] = board
    session['current_multiplier'] = 1.00
    session['bet'] = bet
    session['revealed_cells'] = 0

    return jsonify({
        'success': True,
        'balance': balance,
        'current_multiplier': session['current_multiplier'],
        'history': session['history'],
        'board': board
    })


@app.route('/reveal/<int:row>/<int:col>', methods=['POST'])
def reveal(row, col):
    if 'board' not in session:
        return jsonify({'result': 'error', 'message': 'Игра не начата'})

    board = session['board']
    if board[row][col] == 'M':
        session['history'].insert(0, {'result': 'Проигрыш', 'bet': session['bet'], 'win': 0.00})
        if len(session['history']) > 10:
            session['history'].pop()

        return jsonify({
            'result': 'mine',
            'history': session['history']
        })

    session['revealed_cells'] += 1
    session['current_multiplier'] = 1.0 + (session['revealed_cells'] * (1.0 / (25 - session['revealed_cells'])))

    return jsonify({
        'result': 'safe',
        'current_multiplier': session['current_multiplier']
    })


@app.route('/cashout', methods=['POST'])
def cashout():
    if 'bet' not in session or 'current_multiplier' not in session:
        return jsonify({'success': False, 'message': 'Игра не начата'})

    bet = session['bet']
    multiplier = session['current_multiplier']
    win_amount = bet * multiplier
    balance = get_user_balance()

    if balance is None:
        return jsonify({'success': False, 'message': 'Ошибка авторизации. Пожалуйста, войдите на основном сайте.'})

    balance += win_amount
    update_success = update_user_balance(balance)
    if not update_success:
        return jsonify({'success': False, 'message': 'Не удалось обновить баланс на сервере'})

    session['history'].insert(0, {'result': 'Выигрыш', 'bet': bet, 'win': win_amount})
    if len(session['history']) > 10:
        session['history'].pop()

    session.pop('board', None)
    session.pop('current_multiplier', None)
    session.pop('bet', None)
    session.pop('revealed_cells', None)

    return jsonify({
        'success': True,
        'balance': balance,
        'message': f'Вы забрали {win_amount:.2f} RUB',
        'history': session['history']
    })


if __name__ == '__main__':
    app.run(port=5000)
