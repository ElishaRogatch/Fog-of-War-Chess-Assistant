from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from fow_logger import FowLogger

import tkinter as tk

class InputProcessor:
    def __init__(self, root, logger: FowLogger):
        self.root = root
        self.logger = logger
        self.bias_display = BiasOutput(self.root)
    
    def bias(self) -> dict[str, float]:
        """Process user input to identify bias type."""
        input_value = "" 
        biases: dict[str, float] = {}
        bias_values: dict[str, tuple[int, int]] = {}
        while True:
            if not YesNoInput(self.root, "Would you like to enter a bias?").result:
                break
            #ask user for type of bias
            input_value, confidence, strength = PieceBiasInput(self.root).result
            coefficient = confidence/100 * strength/100
            #process user input, based on whether input is no bias or a piece name
            self.logger.log(f"User input:{input_value}, {coefficient}")
            self.format_bias(input_value, confidence, strength, coefficient, biases, bias_values)
        self.bias_display.close()
        return biases
                

    def format_bias(self, user_input: str, confidence: int, strength: int, coefficient: float, biases: dict[str, float], bias_values: dict[str, tuple[int, int]]): 
        """Takes base user input and converts it to the formatted bias"""
        #TODO change bias to allow for openings as well as pieces
        if user_input:
            if user_input in biases:
                if coefficient == 0:
                    if YesNoInput(self.root, "An entered bias parameter is 0.\nWould you like to remove it?").result:
                        del biases[user_input]
                        del bias_values[user_input]
                elif YesNoInput(self.root, "Entered bias already exists.\nWould you like to replace it?").result:
                    biases[user_input] = coefficient
                    bias_values[user_input] = (confidence, strength)
            else:
                if coefficient == 0:
                    MessageOutput(self.root, "An entered bias parameter is 0.\nBias will not be added")
                else:
                    biases[user_input] = coefficient
                    bias_values[user_input] = (confidence, strength)
            #update bias gui list
            self.bias_display.add_bias(bias_values)
        else:
            MessageOutput(self.root, "No input provided!")
    
 
 
class MessageOutput(tk.Toplevel):
    """Display a popup telling the user a message"""
    def __init__(self, parent, message):
        super().__init__(parent)
        self.parent = parent
        self.iconbitmap("images/icons/Bias.ico")
        self.protocol("WM_DELETE_WINDOW", self.close)
        self.minsize(200, 100)
        self.title("Bias Input")
        
    # Makes this popup window behave like a dependent child of the parent
        self.transient(parent)
        # Grabs the focus and puts it onto this child window
        self.grab_set()

        tk.Label(self, text=message).pack(padx=30, pady=(15,15))

        # OK button
        tk.Button(self, text="OK", command=self.ok).pack(side=tk.BOTTOM, padx=10, pady=5)

        # Pauses code until answered
        self.wait_window(self)


    def ok(self):
        # Store the results from the entry box and the two bias sliders
        self.close()
        
    def close(self):
        self.destroy()
 
 
        
class YesNoInput(tk.Toplevel):
    """Display a popup asking if the user wants to enter another bias"""
    def __init__(self, parent, question):
        super().__init__(parent)
        self.parent = parent
        self.iconbitmap("images/icons/Bias.ico")
        self.protocol("WM_DELETE_WINDOW", self.close)
        self.title("Bias Input")
        self.result = False
        
    # Makes this popup window behave like a dependent child of the parent
        self.transient(parent)
        # Grabs the focus and puts it onto this child window
        self.grab_set()

        tk.Label(self, text=question).pack(padx=30, pady=(15,15))

        # Yes and No buttons
        button_frame = tk.Frame(self)
        tk.Button(button_frame, text="Yes", command=self.yes).pack(side=tk.LEFT, padx=10, pady=5)
        tk.Button(button_frame, text="No", command=self.no).pack(side=tk.RIGHT, padx=10, pady=5)
        button_frame.pack(padx=10, pady=(15,15))

        # Pauses code until answered
        self.wait_window(self)


    def yes(self):
        # Store the results from the entry box and the two bias sliders
        self.result = True
        self.close()

    def no(self):
        self.close() # Result is already False by default
        
    def close(self):
        self.destroy()
    


class PieceBiasInput(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.iconbitmap("images/icons/Bias.ico")
        self.protocol("WM_DELETE_WINDOW", self.close)
        self.title("Bias Input")
        self.result = "", 0, 0
        
        # Makes this popup window behave like a dependent child of the parent
        self.transient(parent)
        # Grabs the focus and puts it onto this child window
        self.grab_set()

        # Variables to hold slider and piece values
        self.confidence_var = tk.IntVar(value=0)
        self.strength_var = tk.IntVar(value=0)
        self.bias_piece = tk.StringVar(value="Pawn")

        tk.Label(self, text="What piece is the opponent biased towards?").pack(padx=10, pady=5)

        # Entry box to type answers into
        self.bias_choose = tk.OptionMenu(self, self.bias_piece, "Pawn", "Bishop", "Knight", "Rook", "Queen")
        self.bias_choose.pack(padx=10, pady=5)
        
        # Labels and sliders for bias values
       
        tk.Label(self, text="How confident are you in the opponents bias?").pack(padx=10, pady=5)
        self.confidence_entry = tk.Entry(self, width=6, textvariable=self.confidence_var) # Entry box to type confidence value into
        self.confidence_entry.pack(padx=10, pady=(5,0))
        self.confidence_slider = tk.Scale(self, variable=self.confidence_var, from_=0, to=100, orient=tk.HORIZONTAL, length=200)
        self.confidence_slider.pack(padx=10, pady=5)
        tk.Label(self, text="How strong would the opponents bias be?").pack(padx=10, pady=5)
        self.strength_entry = tk.Entry(self, width=6, textvariable=self.strength_var) # Entry box to type strength value into
        self.strength_entry.pack(padx=10, pady=(5,0))
        self.strength_slider = tk.Scale(self, variable=self.strength_var, from_=0, to=100, orient=tk.HORIZONTAL, length=200)
        self.strength_slider.pack(padx=10, pady=5)

        # OK and Cancel buttons
        button_frame = tk.Frame(self)
        tk.Button(button_frame, text="OK", command=self.ok).pack(side=tk.LEFT, padx=10, pady=5)
        tk.Button(button_frame, text="Cancel", command=self.cancel).pack(side=tk.RIGHT, padx=10, pady=5)
        button_frame.pack(padx=10, pady=5)

        # Pauses code until answered
        self.wait_window(self)


    def ok(self):
        # Store the results from the entry box and the two bias sliders
        self.result = self.bias_piece.get().lower(), self.confidence_var.get(), self.strength_var.get()
        self.close()

    def cancel(self):
        self.close()
        
    def close(self):
        # Any Tk variables made inside this class need to be deleted when the gui closes as its not the mainloop
        del self.confidence_var
        del self.strength_var
        del self.bias_piece
        self.destroy()
        
        
class BiasOutput(tk.Toplevel):
    """Display the captured pieces for both players."""
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.iconbitmap("images/icons/Bias.ico")
        self.protocol("WM_DELETE_WINDOW", self.close)
        self.minsize(200, 150)
        self.title("User Biases")
        self.bias_text = tk.StringVar()
        
    # Makes this popup window behave like a dependent child of the parent
        self.transient(parent)
        # Grabs the focus and puts it onto this child window
        self.grab_set()

        tk.Label(self, textvariable=self.bias_text, wraplength=280, justify="left").pack(padx=50, pady=5, )


    def add_bias(self, biases):
        text = ""
        sorted_biases = dict(sorted(biases.items(), key=lambda x: x[1][0]*x[1][1], reverse=True))
        for bias in sorted_biases:
            print(f"DEBUG this is {bias}")
            text += f"{bias}\t\t{biases[bias][0]}\t\t{biases[bias][1]}\n"
        self.bias_text.set("Piece\t\tConfidence\tStrength\n\n" + text)
       
    def close(self):
        self.destroy()



if __name__ == "__main__":
    root = tk.Tk()
    root.iconbitmap("images/icons/Bias.ico")
    processor = InputProcessor(root)
    result = processor.bias()

    if result:
        print('\n', "Processed Output:", result, '\n')
    else:
        print("Failed to obtain valid processed output.")