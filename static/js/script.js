var gameHistory = [];

function play(playerChoice) {
    var choices = ['rock', 'paper', 'scissors'];
    var computerChoice = choices[Math.floor(Math.random() * choices.length)];

    var result = '';

    if (playerChoice === computerChoice) {
        result = "It's a tie!";
    } else if ((playerChoice === 'rock' && computerChoice === 'scissors') ||
               (playerChoice === 'paper' && computerChoice === 'rock') ||
               (playerChoice === 'scissors' && computerChoice === 'paper')) {
        result = "You win!";
    } else {
        result = "Computer wins!";
    }

    // Add result to gameHistory
    gameHistory.unshift({ player: playerChoice, computer: computerChoice, result: result }); // добавляем в начало массива
    if (gameHistory.length > 10) {
        gameHistory.pop(); // удаляем последний элемент массива, если количество сохранений больше 10
    }
    updateHistory(); // Update history display

    document.getElementById('result').innerHTML = `You chose ${playerChoice}.<br>Computer chose ${computerChoice}.<br>${result}`;
}

function updateHistory() {
    var historyList = document.getElementById('history');
    historyList.innerHTML = '';
    gameHistory.forEach(function (item) {
        var listItem = document.createElement('li');
        listItem.textContent = `Player: ${item.player}, Computer: ${item.computer}, Result: ${item.result}`;
        historyList.appendChild(listItem);
    });
}
