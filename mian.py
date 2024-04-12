from flask import Flask, request, jsonify, render_template, session
import random
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Генерация безопасного случайного ключа


@app.route('/')
def index():
    # Инициализация баланса и истории, если они еще не установлены
    if 'balance' not in session:
        session['balance'] = 10000
    if 'big_wins' not in session:
        session['big_wins'] = []
    if 'bet_history' not in session:
        session['bet_history'] = []

    return render_template('index.html', balance=session['balance'], big_wins=session['big_wins'],
                           bet_history=session['bet_history'])


@app.route('/bet', methods=['POST'])
def place_bet():
    bet = request.form.get('bet')
    amount = int(request.form.get('amount', 0))

    if amount > session.get('balance', 0):
        return jsonify({'result': 'error', 'message': 'Недостаточно средств на балансе'})

    win = check_bet(bet, amount)

    session['bet_history'].insert(0, {'bet': bet, 'amount': amount, 'win': win})
    if len(session['bet_history']) > 10:
        session['bet_history'].pop()  # Удаление самой старой ставки

    if win > 5000:
        session['big_wins'].insert(0, f'Выигрыш {win}$ ({bet.capitalize()})')
        if len(session['big_wins']) > 10:
            session['big_wins'].pop()

    session.modified = True  # Убедитесь, что сессия будет сохранена после изменений

    return jsonify({
        'result': 'success',
        'win': win,
        'balance': session['balance'],
        'bet_history': session['bet_history'],
        'big_wins': session['big_wins']
    })


def check_bet(bet, amount):
    win_numbers = {
        'red': [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36],
        'black': [2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35],
        'green': [0]
    }
    win_number = random.randint(0, 36)
    if bet in win_numbers and win_number in win_numbers[bet]:
        multiplier = 2 if bet in ['red', 'black'] else 35
        win_amount = multiplier * amount
        session['balance'] += win_amount - amount
        return win_amount
    else:
        session['balance'] -= amount
        return 0


if __name__ == '__main__':
    app.run(debug=True)
