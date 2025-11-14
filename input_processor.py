import json
import requests
import tkinter as tk
from tkinter import simpledialog

class InputProcessor:
    def bias(self):
        root = tk.Tk()
        root.withdraw()
        input_value = simpledialog.askstring("Input", "Hello, what would you like me to do:")
        if input_value:
            print("User input:", input_value)
            result = self.main(input_value)
            return result
        else:
            print("No input provided.")
            return None

    def main(self, user_input): 
        #search user input for piece name substring 
        pieces = ["knight", "bishop", "rook", "queen", "king"]
        matches = [p for p in pieces if p in user_input.lower()]
        result = {"piece" : matches[0]} if matches else {"piece" : None}
        return result

if __name__ == "__main__":
    processor = InputProcessor()
    result = processor.bias()

    if result:
        print('\n', "Processed Output:", result, '\n')
    else:
        print("Failed to obtain valid processed output.")
