from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import requests
import random
from config import secret_key

app = Flask(__name__)
app.secret_key = secret_key

# Define the multipliers based on the number of revealed cells
multipliers = {
    2: [1.05, 1.15, 1.26, 1.39, 1.53, 1.70],
    3: [1.10, 1.26, 1.45, 1.68, 1.96, 2.30],
    4: [1.15, 1.39, 1.68, 2.05, 2.53, 3.17],
    5: [1.21, 1.53, 1.96, 2.53, 3.32, 4.43],
    6: [1.28, 1.70, 2.30, 3.17, 4.43, 6.33],
    7: [1.35, 1.90, 2.73, 4.01, 6.01, 9.25],
    8: [1.43, 2.14, 3.28, 5.16, 8.33, 13.88],
    9: [1.51, 2.42, 3.98, 6.74, 11.80, 21.45],
    10: [1.62, 2.77, 4.90, 8.99, 17.16, 34.32],
    11: [1.73, 3.20, 6.13, 12.26, 25.74, 57.20],
    12: [1.86, 3.73, 7.80, 17.16, 40.04, 100.11],
    13: [2.02, 4.41, 10.14, 24.79, 65.07, 185.92],
    14: [2.20, 5.29, 13.52, 37.18, 111.55, 371.83],
    15: [2.42, 6.47, 18.59, 58.43, 204.51, 818.03],
    16: [2.69, 8.08, 26.56, 97.38, 409.02, 2050],
    17: [3.03, 10.39, 39.84, 175.29, 920.29, 6140],
    18: [3.46, 13.86, 63.74, 350.58, 2450, 24540],
    19: [4.04, 19.40, 111.55, 818.03, 8590, 172000],
    20: [4.85, 29.10, 223.10, 2450, 51540],
    21: [6.06, 48.50, 557.75, 12270],
    22: [8.08, 97, 2230],
    23: [12.13, 291],
    24: [24.25]
}

# URL основного сервера
BASE_URL = 'http://127.0.0.1:1000/api'

def get_balance():
    if 'session_id' not in session:
        return 0  # Возвращаем 0, если session_id не найден
    response = requests.get(f'{BASE_URL}/get_balance', cookies={'session': session['session_id']})
    if response.status_code == 200:
        return response.json().get('balance', 0)
    return 0

def update_balance(new_balance):
    if 'session_id' not in session:
        return False  # Возвращаем False, если session_id не найден
    response = requests.post(f'{BASE_URL}/update_balance', json={'balance': new_balance}, cookies={'session': session['session_id']})
    return response.status_code == 200

@app.route('/')
def index():
    if 'session_id' not in session:
        session['session_id'] = request.cookies.get('session')  # Инициализация session_id
    session['balance'] = get_balance()
    if 'history' not in session:
        session['history'] = []
    return redirect(url_for('play'))

@app.route('/play', methods=['GET', 'POST'])
def play():
    if request.method == 'POST':
        bet = float(request.form['bet'])
        num_mines = int(request.form['num_mines'])

        session['balance'] = get_balance()  # Получаем актуальный баланс перед ставкой
        if session['balance'] < bet:
            return jsonify(success=False, message="Недостаточно средств на балансе")

        session['balance'] -= bet
        if not update_balance(session['balance']):
            return jsonify(success=False, message="Ошибка при обновлении баланса")

        # Generate board with mines
        board = [['' for _ in range(5)] for _ in range(5)]
        mines = random.sample(range(5 * 5), num_mines)
        for mine in mines:
            board[mine // 5][mine % 5] = 'M'

        session['board'] = board
        session['bet'] = bet
        session['num_mines'] = num_mines
        session['revealed'] = 0
        session['current_multiplier'] = 1.0

        return jsonify(success=True, balance=round(session['balance'], 2), board=board, current_multiplier=session['current_multiplier'], history=list(reversed(session['history'])))

    return render_template('mines.html',
                           balance=round(session['balance'], 2),
                           board=session.get('board', [['' for _ in range(5)] for _ in range(5)]),
                           bet=session.get('bet', 0),
                           num_mines=session.get('num_mines', 0),
                           revealed=session.get('revealed', 0),
                           current_multiplier=session.get('current_multiplier', 1.0),
                           history=list(reversed(session.get('history', []))))

@app.route('/reveal/<int:row>/<int:col>', methods=['POST'])
def reveal(row, col):
    if 'board' not in session or 'bet' not in session:
        return jsonify(result='error', message='Игра не инициализирована')

    board = session['board']
    if board[row][col] == 'M':
        session['history'].insert(0, {'result': 'loss', 'bet': session['bet'], 'win': 0})
        session['history'] = session['history'][:5]  # Keep only the last 5 entries
        session['current_multiplier'] = 1.0  # Reset multiplier on loss
        return jsonify(result='mine', balance=round(session['balance'], 2), current_multiplier=session['current_multiplier'], history=list(reversed(session['history'])))

    session['revealed'] += 1
    board[row][col] = 'R'
    session['board'] = board

    if session['revealed'] <= len(multipliers[session['num_mines']]):
        session['current_multiplier'] = multipliers[session['num_mines']][session['revealed'] - 1]
    else:
        session['current_multiplier'] *= 1.5  # Arbitrary increase if all predefined multipliers are used

    return jsonify(result='safe', current_multiplier=session['current_multiplier'], history=list(reversed(session['history'])))

@app.route('/cashout', methods=['POST'])
def cashout():
    if 'bet' not in session or 'current_multiplier' not in session:
        return jsonify(success=False, message='Игра не инициализирована')

    win_amount = round(session['bet'] * session['current_multiplier'], 2)
    session['balance'] = get_balance()  # Получаем актуальный баланс перед обновлением
    session['balance'] += win_amount
    if not update_balance(session['balance']):
        return jsonify(success=False, message="Ошибка при обновлении баланса")

    session['history'].insert(0, {'result': 'win', 'bet': session['bet'], 'win': win_amount})
    session['history'] = session['history'][:5]  # Keep only the last 5 entries
    session.pop('bet', None)
    session.pop('num_mines', None)
    session.pop('revealed', None)
    session.pop('current_multiplier', None)
    session.pop('board', None)

    return jsonify(success=True, balance=round(session['balance'], 2), current_multiplier=1.0, message=f"Вы выиграли {win_amount:.2f} RUB", history=list(reversed(session['history'])))

@app.route('/restart', methods=['POST'])
def restart():
    session.pop('bet', None)
    session.pop('num_mines', None)
    session.pop('revealed', None)
    session.pop('current_multiplier', None)
    session.pop('board', None)
    return jsonify(success=True)


if __name__ == '__main__':
    app.run(debug=True)
