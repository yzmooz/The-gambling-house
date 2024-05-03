from flask import Flask, request, jsonify, render_template, session
import random
import os

app = Flask(__name__)
app.secret_key = os.getlogin() + '1'

# Инициализация глобальных переменных
previous_win_number = 0
current_win_number = 0


@app.route('/')
def index():
    # Инициализация баланса и истории, если они еще не установлены
    if 'balance' not in session:
        session['balance'] = 10000
    if 'big_wins' not in session:
        session['big_wins'] = []
    if 'bet_history' not in session:
        session['bet_history'] = []

    return render_template('roulette.html', balance=session['balance'], big_wins=session['big_wins'],
                           bet_history=session['bet_history'])


@app.route('/bet', methods=['POST'])
def place_bet():
    global previous_win_number, current_win_number  # Объявляем переменные как глобальные

    # Получение ставки и суммы
    bet = request.form.get('bet')
    amount = int(request.form.get('amount', 0))

    # Проверка баланса
    if amount > session.get('balance', 0):
        return jsonify({'result': 'error', 'message': 'Недостаточно средств на балансе'})

    # Проверка ставки и получение выигрышного значения и числа
    win, win_number = check_bet(bet, amount)

    # Сохраняем предыдущий выигрышный номер
    previous_win_number = current_win_number
    # Обновляем текущий выигрышный номер
    current_win_number = win_number

    rotation_angle = calculate_angle(current_win_number)

    # Сохраняем историю ставок
    session['bet_history'].insert(0, {'bet': bet, 'amount': amount, 'win': win})
    if len(session['bet_history']) > 10:
        session['bet_history'].pop()  # Удаляем старую ставку, если их более 10
    print(win_number)
    print(rotation_angle)
    # Проверяем крупные выигрыши
    if win > 5000:
        session['big_wins'].insert(0, f'Выигрыш {win}$ ({bet.capitalize()})')
        if len(session['big_wins']) > 10:
            session['big_wins'].pop()  # Удаляем старые крупные выигрыши, если их более 10

    # Возвращаем результат в виде JSON
    return jsonify({
        'result': 'success',
        'win': win,
        'balance': session['balance'],
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

    # Вычислим разницу между позициями
    index_diff = numbers.index(num2)  # Найдем позицию чисела в списке

    # Вычислим угол между числами
    angle = index_diff * sector_size

    # Угол должен быть положительным, если он отрицательный, сделаем его положительным
    if angle <= 0:
        angle += 360

    return angle


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
        return win_amount, win_number

    elif bet.isdigit() and int(bet) == win_number:
        print("Type of bet:", type(bet))
        multiplier = 35
        win_amount = multiplier * amount
        session['balance'] += win_amount - amount
        return win_amount, win_number
    else:
        session['balance'] -= amount
        return 0, win_number


if __name__ == '__main__':
    app.run(port=1488)
