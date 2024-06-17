import threading
import home
import roulette
import rps
import dice
import mines


def run_home():
    home.app.run(port=1000)


def run_roulette():
    roulette.app.run(port=2000)


def run_rock_paper_scissors():
    rps.app.run(port=3000)


def run_dice():
    dice.app.run(port=4000)


def run_mines():
    mines.app.run(port=5000)


if __name__ == '__main__':
    threads = [
        threading.Thread(target=run_home),
        threading.Thread(target=run_roulette),
        threading.Thread(target=run_rock_paper_scissors),
        threading.Thread(target=run_dice),
        threading.Thread(target=run_mines),
    ]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()
