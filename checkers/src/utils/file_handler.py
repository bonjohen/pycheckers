import tkinter as tk
from tkinter import filedialog
import logging

def open_file_dialog():
    """Shows an open file dialog and returns the selected filename"""
    root = tk.Tk()
    root.withdraw()
    filename = filedialog.askopenfilename(
        title="Load Game",
        filetypes=(("Text Files", "*.txt"), ("All Files", "*.*"))
    )
    root.destroy()
    return filename

def save_file_dialog():
    """Shows a save file dialog and returns the selected filename"""
    root = tk.Tk()
    root.withdraw()
    filename = filedialog.asksaveasfilename(
        title="Save Game",
        defaultextension=".txt",
        filetypes=(("Text Files", "*.txt"), ("All Files", "*.*"))
    )
    root.destroy()
    return filename

def save_game(filename, move_history):
    """Saves the game move history to a file"""
    try:
        with open(filename, "w") as f:
            for line in move_history:
                f.write(line + "\n")
        logging.debug(f"Game saved to {filename}")
        return True
    except Exception as e:
        logging.error(f"Error saving game: {e}")
        return False

def load_game(filename):
    """Loads a game from a file and returns the move history"""
    try:
        with open(filename, "r") as f:
            move_history = f.read().splitlines()
        logging.debug(f"Game loaded from {filename}")
        return move_history
    except Exception as e:
        logging.error(f"Error loading game: {e}")
        return None