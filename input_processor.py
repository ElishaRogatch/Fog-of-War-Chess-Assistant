from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from fow_logger import FowLogger

import tkinter as tk
from gui_io import YesNoIO, MessageOutput

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
            if not self.bias_yes_no("Would you like to enter a bias?").result:
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
                    if self.bias_yes_no("An entered bias parameter is 0.\nWould you like to remove it?").result:
                        del biases[user_input]
                        del bias_values[user_input]
                elif self.bias_yes_no("Entered bias already exists.\nWould you like to replace it?").result:
                    biases[user_input] = coefficient
                    bias_values[user_input] = (confidence, strength)
            else:
                if coefficient == 0:
                    self.bias_message("An entered bias parameter is 0.\nBias will not be added")
                else:
                    biases[user_input] = coefficient
                    bias_values[user_input] = (confidence, strength)
            #update bias gui list
            self.bias_display.add_bias(bias_values)
        else:
            self.bias_message("No input provided!")
            
    def bias_message(self, message_to_show):
        return MessageOutput(
            parent=self.root,
            message=message_to_show,
            title="Bias Input",
            icon_path="images/icons/Bias.ico",
            min_size=(200,100), 
            label_padding=(30,15)
        )
            
    def bias_yes_no(self, question_to_ask):
        return YesNoIO(
            parent=self.root, 
            question=question_to_ask, 
            title="Bias Input",
            icon_path="images/icons/Bias.ico"
        )
        

class PieceBiasInput(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.iconbitmap("images/icons/Bias.ico")
        self.protocol("WM_DELETE_WINDOW", self.cancel)
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