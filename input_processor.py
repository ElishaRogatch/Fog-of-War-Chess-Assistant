import tkinter as tk
from tkinter.simpledialog import _QueryDialog
from tkinter import messagebox

class InputProcessor:
    def __init__(self, root):
        self.root = root
        self.enter_bias = tk.BooleanVar(root, value=True)
    
    def bias(self):
        """Process user input to identify bias type."""
        input_value = "no bias" 
        while True:
            self.ask_yesno(self.root)
            if not self.enter_bias.get():
                break
            #ask user for type of bias
            bias_dialog = _QueryString("Bias Input", "What piece is the opponent biased towards?")
            input_value = bias_dialog.result
        #process user input, based on whether input is no bias or a piece name
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
        #TODO change bias to allow for openings as well as pieces
        #search user input for piece name substring 
        pieces = ["knight", "bishop", "rook", "queen", "king"]
        matches = [p for p in pieces if p in user_input.lower()]
        result = {"piece" : matches[0]} if matches else {"piece" : None}
        return result
    
    def show_slider(self):
        """Display a popup with the top move suggestions and their scores."""
        suggestion_box = tk.Toplevel()
        suggestion_box.title("Top 5 Move Suggestions and Scores")
        suggestion_box.geometry("400x150")
        suggestion_box.grab_set()
        suggestion_box.iconbitmap("images/icons/Bias.ico")
        tk.Button(suggestion_box, text="Ok", command=suggestion_box.destroy).pack(pady=10,side= tk.BOTTOM)
        
    def ask_yesno(self, root):
        """Display a popup with the top move suggestions and their scores."""
        suggestion_box = tk.Toplevel(root)
        suggestion_box.title("Bias Input")
        suggestion_box.geometry("400x150")
        suggestion_box.grab_set()
        suggestion_box.iconbitmap("images/icons/Bias.ico")
        button_frame = tk.Frame(suggestion_box)
        button_frame.pack(pady=10, side=tk.BOTTOM)
        tk.Label(suggestion_box, text= "Would you like to enter a bias?").pack(pady=(10, 0))
        tk.Button(button_frame, text="Yes", command= lambda: (self.enter_bias.set(True), suggestion_box.destroy()) ).pack(padx=10,side= tk.LEFT)
        tk.Button(button_frame, text="No", command= lambda: (self.enter_bias.set(False), suggestion_box.destroy()) ).pack(padx=10,side= tk.RIGHT)
        root.wait_window(suggestion_box)
    
        
        

if __name__ == "__main__":
    root = tk.Tk()
    root.iconbitmap("images/icons/BIAS.ico")
    processor = InputProcessor(root)
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