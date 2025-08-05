import tkinter as tk
import random
import requests
import os
from playsound import playsound
from gtts import gTTS
WORDLIST_FILENAME = "words.txt"
STATS_FILENAME = "hangman_stats.txt"
MAX_WRONG = 6
def loadWords():
    word_dict = {}
    with open(WORDLIST_FILENAME, 'r') as inFile:
        for line in inFile:
            if ':' in line:
                category, words = line.strip().split(":")
                word_dict[category.strip()] = words.strip().split(",")
    return word_dict
def fetch_full_definition(word):
    try:
        url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            meaning_data = data[0]['meanings'][0]
            definition = meaning_data['definitions'][0]['definition']
            part_of_speech = meaning_data['partOfSpeech']
            example = meaning_data['definitions'][0].get('example', "No example available.")
            return definition, part_of_speech, example
    except:
        pass
def load_stats():
    if os.path.exists(STATS_FILENAME):
        with open(STATS_FILENAME, 'r') as f:
            lines = f.readlines()
            return int(lines[0].strip()), int(lines[1].strip())
    return 0, 0
def save_stats(wins, losses):
    with open(STATS_FILENAME, 'w') as f:
        f.write(f"{wins}\n{losses}\n")
class HangmanGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Hangman Game 🎯")
        self.root.configure(bg="#f4f4f4")
        self.wordlist = loadWords()
        self.wins, self.losses = load_stats()
        self.setup_widgets()
        self.category_var.set("Select Category")
        self.update_category_menu()
    def setup_widgets(self):
        self.category_var = tk.StringVar(self.root)
        self.category_menu = tk.OptionMenu(self.root, self.category_var, "")
        self.category_menu.config(font=('Helvetica', 12), bg="#eeeeee")
        self.category_menu.pack(pady=5)
        self.word_display = tk.Label(self.root, text="", font=('Helvetica', 26, 'bold'), bg="#f4f4f4", fg="#222")
        self.word_display.pack(pady=10)
        self.entry = tk.Entry(self.root, font=('Helvetica', 18), justify='center')
        self.entry.pack(pady=5)
        self.submit_btn = tk.Button(self.root, text="Guess", font=('Helvetica', 12), command=self.make_guess, bg="#4CAF50", fg="white")
        self.submit_btn.pack(pady=5)
        self.hint_btn = tk.Button(self.root, text="Get a Hint", font=('Helvetica', 12), command=self.show_hint, bg="#2196F3", fg="white")
        self.hint_btn.pack(pady=5)
        self.meaning_label = tk.Label(self.root, text="", font=('Helvetica', 12), bg="#f4f4f4", fg="#444", wraplength=500)
        self.meaning_label.pack(pady=5)
        self.canvas = tk.Canvas(self.root, width=200, height=250, bg="#f4f4f4", highlightthickness=0)
        self.canvas.pack(pady=10)
        self.stats_label = tk.Label(self.root, text="", font=('Helvetica', 14), bg="#f4f4f4", fg="#555")
        self.stats_label.pack(pady=5)
        self.result_label = tk.Label(self.root, text="", font=('Helvetica', 18), bg="#f4f4f4")
        self.result_label.pack(pady=10)
        self.new_game_btn = tk.Button(self.root, text="Play Game", font=('Helvetica', 12), command=self.new_game, bg="#FF5722", fg="white")
        self.new_game_btn.pack(pady=10)
    def update_category_menu(self):
        menu = self.category_menu["menu"]
        menu.delete(0, "end")
        for category in self.wordlist:
            menu.add_command(label=category, command=lambda value=category: self.category_var.set(value))
    def new_game(self):
        selected_category = self.category_var.get()
        if selected_category not in self.wordlist:
            self.result_label.config(text="Please select a category to start.", fg="red")
            return
        self.secretWord = random.choice(self.wordlist[selected_category]).lower()
        self.lettersGuessed = set()
        self.wrongGuesses = 0
        self.hint_stage = 0
        self.definition, self.part_of_speech, self.example = fetch_full_definition(self.secretWord)
        self.meaning_label.config(text="")
        self.canvas.delete("all")
        self.draw_gallows()
        self.update_display()
        self.result_label.config(text="")
        self.entry.config(state=tk.NORMAL)
        self.submit_btn.config(state=tk.NORMAL)
        self.hint_btn.config(state=tk.NORMAL)

    def update_display(self):
        displayed = ' '.join([c if c in self.lettersGuessed else '_' for c in self.secretWord])
        self.word_display.config(text=displayed)
        self.stats_label.config(text=f"Wins: {self.wins}  Losses: {self.losses}")
        self.draw_hangman()

    def draw_gallows(self):
        self.canvas.create_line(20, 230, 180, 230, width=2)
        self.canvas.create_line(50, 230, 50, 20, width=2)
        self.canvas.create_line(50, 20, 130, 20, width=2)
        self.canvas.create_line(130, 20, 130, 50, width=2)

    def draw_hangman(self):
        self.canvas.delete("hangman")
        color = "#D32F2F" if self.wrongGuesses >= MAX_WRONG else "#388E3C"
        if self.wrongGuesses >= 1:
            self.canvas.create_oval(110, 50, 150, 90, fill=color, tags="hangman")
        if self.wrongGuesses >= 2:
            self.canvas.create_line(130, 90, 130, 150, fill=color, width=3, tags="hangman")
        if self.wrongGuesses >= 3:
            self.canvas.create_line(130, 100, 110, 130, fill=color, width=3, tags="hangman")
        if self.wrongGuesses >= 4:
            self.canvas.create_line(130, 100, 150, 130, fill=color, width=3, tags="hangman")
        if self.wrongGuesses >= 5:
            self.canvas.create_line(130, 150, 110, 190, fill=color, width=3, tags="hangman")
        if self.wrongGuesses >= 6:
            self.canvas.create_line(130, 150, 150, 190, fill=color, width=3, tags="hangman")

    def make_guess(self):
        guess = self.entry.get().lower()
        self.entry.delete(0, tk.END)

        if not guess.isalpha():
            return

        if len(guess) == 1:
            if guess in self.lettersGuessed:
                return
            self.lettersGuessed.add(guess)
            if guess not in self.secretWord:
                self.wrongGuesses += 1
        elif guess == self.secretWord:
            self.lettersGuessed.update(self.secretWord)
        else:
            self.wrongGuesses += 1

        self.update_display()
        self.check_game_end()

    def show_hint(self):
      
        if self.hint_stage == 0:
            letters = random.sample([c for c in self.secretWord if c not in self.lettersGuessed], 2)
            hint_text = f"Hint: The word contains the letters: '{letters[0]}' and '{letters[1]}'."
            self.meaning_label.config(text=hint_text)
            self.hint_stage += 1
        else:
            self.meaning_label.config(text="No more hints available.")
            self.hint_btn.config(state=tk.DISABLED)

    def check_game_end(self):
        if all(c in self.lettersGuessed for c in self.secretWord):
            self.result_label.config(text="🎉 You Win! 😊", fg="#2E7D32")
            self.wins += 1
            self.game_over()
        elif self.wrongGuesses >= MAX_WRONG:
            self.result_label.config(text=f"💀 You Lost 😢\nThe word was: {self.secretWord}", fg="#C62828")
            self.losses += 1
            self.game_over()

    def game_over(self):
        save_stats(self.wins, self.losses)
        self.entry.config(state=tk.DISABLED)
        self.submit_btn.config(state=tk.DISABLED)
        self.hint_btn.config(state=tk.DISABLED)

        self.meaning_label.config(text=f"Meaning: {self.definition}")

        try:
            tts = gTTS(text=f"The word was {self.secretWord}. Meaning: {self.definition}", lang='en')
            tts.save("meaning.mp3")
            playsound("meaning.mp3")
            os.remove("meaning.mp3")
        except:
            print("TTS playback failed.")

if __name__ == "__main__":
    root = tk.Tk()
    game = HangmanGame(root)
    root.mainloop()
