import json
import requests
import tkinter as tk
from tkinter.simpledialog import _QueryDialog

class InputProcessor:
    def bias(self):
        #root = tk.Tk()
        #root.withdraw()
        bias_dialog = _QueryString("Input", "Hello, what would you like me to do:")
        input_value = bias_dialog.result 
        if input_value:
            print("User input:", input_value)
            if input_value.lower() == "no bias":
                return None
            result = self.main(input_value)
            return result
        else:
            print("No input provided.")
            return {"piece" : None}

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
        
class _QueryString(_QueryDialog): # overwrite class to allow for custom icon
    def __init__(self, *args, **kw):
        if "show" in kw:
            self.__show = kw["show"]
            del kw["show"]
        else:
            self.__show = None
        _QueryDialog.__init__(self, *args, **kw)

    def body(self, master):
        entry = _QueryDialog.body(self, master)
        self.iconbitmap("images/icons/Bias.ico")
        if self.__show is not None:
            entry.configure(show=self.__show)
        return entry

    def getresult(self):
        return self.entry.get()
