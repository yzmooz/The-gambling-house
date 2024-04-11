from flask import Flask, request, jsonify, render_template
import random

app = Flask(__name__)

balance = 10000  # Для демонстрации, в реальном приложении используйте БД или сессии
big_wins = []  # История больших выигрышей
bet_history = []  # История последних 10 ставок

@app.route('/')
def index():
    return render_template('index.html', balance=balance, big_wins=big_wins, bet_history=bet_history)


@app.route('/bet', methods=['POST'])
def place_bet():
    """Обрабатывает ставки пользователя"""
    global balance, big_wins, bet_history
    bet = request.form.get('bet')
    amount = int(request.form.get('amount', 0))

    if amount > balance:
        return jsonify({'result': 'error', 'message': 'Недостаточно средств на балансе'})

    win = check_bet(bet, amount)
    balance += win

    # Добавляем в историю ставок
    bet_history.insert(0, {'bet': bet, 'amount': amount, 'win': win})
    if len(bet_history) > 10:
        bet_history.pop(-1)  # Удаляем самую старую ставку, если их больше 10

    # Добавляем в историю больших выигрышей, если выигрыш больше 1000
    if win > 1000:
        big_wins.insert(0, f'Выигрыш {win}$ ({bet.capitalize()})')
        if len(big_wins) > 10:
            big_wins.pop()  # Удаляем самый старый выигрыш, если их больше 10
    return jsonify({'result': 'success', 'win': win, 'balance': balance})

def check_bet(bet, amount):
    """Проверяет ставку и возвращает выигрыш или проигрыш"""
    global balance
    win_numbers = {
        'red': [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36],
        'black': [2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35],
        'green': [0]
    }
    win_number = random.randint(0, 36)
    if bet in ['red', 'black']:
        if win_number in win_numbers[bet]:
            balance += 2 * amount
            return 2 * amount
        else:
            balance -= amount
            return 0
    elif bet == 'green':
        if win_number in win_numbers[bet]:
            balance += 35 * amount
            return 35 * amount
        else:
            balance -= amount
            return 0
    elif win_number == int(bet):
        balance += 35 * amount
        return 35 * amount
    else:
        balance -= amount
        return 0


if __name__ == '__main__':
    app.run()