from flask import Flask, render_template, request, jsonify
import random

app = Flask(__name__)

# Баланс игрока
balance = 100


@app.route('/')
def index():
    return render_template('index.html', balance=balance)


@app.route('/play', methods=['POST'])
def play():
    global balance
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

    response = {
        'result': result,
        'computer_choice': computer_choice,
        'balance': balance,
        'result_class': result_class,
        'amount': amount
    }
    return jsonify(response)


if __name__ == '__main__':
    app.run(debug=True)
