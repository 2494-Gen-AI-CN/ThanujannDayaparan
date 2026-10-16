import random

from api import get_pokemon_data

def get_random_pokemon(pokemon_data, exclude=None):
    choices = [pokemon for pokemon in pokemon_data if pokemon != exclude]
    return random.choice(choices)


def play_game():
    pokemon_data = get_pokemon_data()
    high_score = 0

    while True:
        champion = get_random_pokemon(pokemon_data)
        score = 0

        while True:
            challenger = get_random_pokemon(pokemon_data, exclude=champion)

            print(f"\nChampion: {champion['name']}")
            print(f"Challenger: {challenger['name']}")

            guess = input("Who has the higher base stat total? (1 or 2): ").strip()
            
            while guess not in ("1", "2"):
                guess = input("Please enter 1 or 2: ")

            champion_total = champion["base_stats_total"]
            challenger_total = challenger["base_stats_total"]

            print(f"{champion['name']}: {champion_total} | {challenger['name']}: {challenger_total}")

            if champion_total == challenger_total:
                print("Tie. Champion stays.")
                continue

            correct = (champion_total > challenger_total and guess == "1") or (challenger_total > champion_total and guess == "2")

            if not correct:
                print(f"Wrong! Game over. Final score: {score}.")
                break

            score += 1
            print(f"Correct! Your score is {score}.")

            if challenger_total > champion_total:
                    champion = challenger
                    print(f"{champion['name']} is the new champion!")

            high_score = max(high_score, score) 
            print(f"Current high score: {high_score}")
            if input("Do you want to play again? (y/n): ").strip().lower() != "y":
                print("Thanks for playing!")
                break

if __name__ == "__main__":
    import tkinter as tk
    from gui import Game  

    root = tk.Tk()
    Game(root)
    root.mainloop()
