import tkinter as tk
# Used to wrap raw data into a file object for PIL to read
from io import BytesIO
from tkinter import ttk
import requests
import random
# using PIL for image processing and resizing images to fit the GUI buttons
from PIL import Image, ImageTk
from pathlib import Path
from api import get_pokemon_data

SPRITE_SIZE = (256, 256)  
HIGH_SCORE_FILE = Path(__file__).with_name("high_score.txt")

# Cache for loaded sprites to avoid re-downloading and processing images
_sprite_cache = {}


# Returns a PhotoImage for the Pokémon
def load_sprite(pokemon):
    name = pokemon["name"]
    if name not in _sprite_cache:
        response = requests.get(pokemon["sprite"], timeout=10)
        response.raise_for_status()
        # Load the image, convert to RGBA, resize, and cache it
        img = Image.open(BytesIO(response.content)).convert("RGBA")
        # Resizing the image to the SPRITE_SIZE
        img = img.resize(SPRITE_SIZE, Image.NEAREST)
        # Cache the PhotoImage to avoid re-downloading and processing  
        _sprite_cache[name] = ImageTk.PhotoImage(img)
    return _sprite_cache[name]

# Load the high score from a file, returning 0 if the file doesn't exist or is invalid
def load_high_score():
    try:
        return int(HIGH_SCORE_FILE.read_text())
    except (FileNotFoundError, ValueError):
        return 0 

def save_high_score(score):
    HIGH_SCORE_FILE.write_text(str(score))

class Game:
    def __init__(self, root):
        self.root = root
        self.pokemon_data = get_pokemon_data()
        self.score = 0
        self.high_score = load_high_score()

        root.title("Pokémon Higher or Lower")
        root.geometry("800x700")

        # Make columns expand equally when resizing the window
        root.columnconfigure(0, weight=1, uniform="cols")
        root.columnconfigure(1, weight=1, uniform="cols")

        # set styles for buttons
        style = ttk.Style()
        style.configure("Choice.TButton", font=("Arial", 16, "bold"))
        style.configure("Again.TButton", font=("Arial", 12))

        # StringVars to hold dynamic text for the GUI
        self.status = tk.StringVar()
        self.score_text = tk.StringVar()
        self.left_total = tk.StringVar()
        self.right_total = tk.StringVar()

        ttk.Label(root, textvariable=self.status, font=("Arial", 14)).grid(row=0, column=0, columnspan=2, pady=(10, 20))
        ttk.Label(root, textvariable=self.score_text, font=("Arial", 14), relief="solid", background="lightblue", padding=(10, 10)).grid(row=1, column=0, columnspan=2, pady=(0, 20))

        # Create labels for the Pokémon images and names
        self.left_label = ttk.Label(root, compound="top", font=("Arial", 18, "bold"))
        self.right_label = ttk.Label(root, compound="top", font=("Arial", 18, "bold"))
        self.left_label.grid(row=2, column=0, padx=20, pady=10)
        self.right_label.grid(row=2, column=1, padx=20, pady=10)

        ttk.Label(root, textvariable=self.left_total, font=("Arial", 14)).grid(row=3, column=0)
        ttk.Label(root, textvariable=self.right_total, font=("Arial", 14)).grid(row=3, column=1)

        # Frame holds both buttons so they sit together in the middle
        button_frame = ttk.Frame(root)
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)

        # Buttons for the player to make their choice
        self.higher_btn = ttk.Button(button_frame, text="Higher", style="Choice.TButton", command=lambda: self.guess("higher"))
        self.lower_btn = ttk.Button(button_frame, text="Lower", style="Choice.TButton", command=lambda: self.guess("lower"))
        self.higher_btn.grid(row=0, column=0, padx=20, pady=20)
        self.lower_btn.grid(row=0, column=1, padx=20, pady=20)

        self.again_btn = ttk.Button(root, text="Play again", style="Again.TButton", command=self.restart)

        self.restart()

    def set_buttons(self, enabled):
        state = ["!disabled"] if enabled else ["disabled"]
        self.higher_btn.state(state)
        self.lower_btn.state(state)
 
    def update_score_text(self):
        self.score_text.set(f"Score: {self.score}   High score: {self.high_score}")
 
    def pick_mystery(self):
        # Never pick a Pokémon with the same total, so there are no ties
        current_total = self.current["base_stats_total"]
        options = [p for p in self.pokemon_data if p["base_stats_total"] != current_total]
        return random.choice(options)
 
    def show_round(self):
        self.left_label.config(image=load_sprite(self.current), text=self.current["name"])
        self.right_label.config(image=load_sprite(self.mystery), text=self.mystery["name"])
        self.left_total.set(f"Base stat total: {self.current['base_stats_total']}")
        self.right_total.set("Base stat total: ???")
        self.status.set(f"Does {self.mystery['name']} have a higher or lower total than {self.current['name']}?")
        self.update_score_text()
        self.set_buttons(True)
 
    def guess(self, choice):
        self.set_buttons(False)
 
        current_total = self.current["base_stats_total"]
        mystery_total = self.mystery["base_stats_total"]
        self.right_total.set(f"Base stat total: {mystery_total}")
 
        is_higher = mystery_total > current_total
        correct = is_higher == (choice == "higher")
 
        if correct:
            self.score += 1
            if self.score > self.high_score:
                self.high_score = self.score
                save_high_score(self.high_score)
            self.update_score_text()
            self.status.set("Correct!")
            self.root.after(1500, self.advance)
        else:
            self.update_score_text()
            self.status.set(f"Wrong! Game over. Final score: {self.score}")
            self.again_btn.grid(row=5, column=0, columnspan=2, pady=10)
 
    def advance(self):
        # The Pokémon just guessed becomes the new reference
        self.current = self.mystery
        self.mystery = self.pick_mystery()
        self.show_round()
 
    def restart(self):
        self.score = 0
        self.again_btn.grid_remove()
        self.current = random.choice(self.pokemon_data)
        self.mystery = self.pick_mystery()
        self.show_round()
 
 
if __name__ == "__main__":
    root = tk.Tk()
    Game(root)
    root.mainloop()
 
    
    