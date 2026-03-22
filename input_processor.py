import tkinter as tk

class InputProcessor:
    def __init__(self, root):
        self.root = root
        self.enter_bias = tk.BooleanVar(self.root, value=True)
    
    def bias(self):
        """Process user input to identify bias type."""
        input_value = "" 
        biases = {}
        while True:
            if not YesNoInput(self.root, "Would you like to enter a bias?").result:
                break
            #ask user for type of bias
            input_value, coefficient = PieceBiasInput(self.root).result
            #process user input, based on whether input is no bias or a piece name
            print(f"User input:{input_value}, {coefficient}") #DEVLOG
            self.format_bias(input_value, coefficient, biases)
        return biases
                

    # Idea: {"piece" : [("bishop", 0.5), "pawn"], }
    def format_bias(self, user_input, coefficient, biases): 
        """Takes base user input and converts it to the formatted bias"""
        #TODO change bias to allow for openings as well as pieces
        if user_input:
            user_input = user_input.lower() # Standardize input
            pieces = ["pawn", "knight", "bishop", "rook", "queen", "king"]
            matches = [p for p in pieces if p in user_input]
            if matches:
                if len(matches) == 1:
                    if matches[0] in biases:
                        if YesNoInput(self.root, "Entered bias already exists.\nWould you like to replace it?").result:
                            biases[matches[0]] = coefficient
                    else:
                        biases[matches[0]] = coefficient
                    #TODO TODO ACTUALLY MAKE THIS!!!!CLIENT NEEDS THIS! #update bias gui list
                else:
                    MessageOutput(self.root, "Multiple pieces detected in input.\nPlease enter them one at a time.")
            else: # No piece matches found in input
                MessageOutput(self.root, "Entered bias does not match a known piece.")
        else:
            MessageOutput(self.root, "No input provided!")
    
 
 
class MessageOutput(tk.Toplevel):
    """Display a popup asking if the user wants to enter another bias"""
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
        self.result = None, 0
        
        # Makes this popup window behave like a dependent child of the parent
        self.transient(parent)
        # Grabs the focus and puts it onto this child window
        self.grab_set()

        # Variables to hold slider values
        self.confidence_var = tk.IntVar(value=0)
        self.strength_var = tk.IntVar(value=0)

        tk.Label(self, text="What piece is the opponent biased towards?").pack(padx=10, pady=5)

        # Entry box to type answers into
        self.entry = tk.Entry(self, width=32)
        self.entry.pack(padx=10, pady=5)
        
        # Labels and sliders for bias values
        tk.Label(self, text="How confident are you in the opponents bias?").pack(padx=10, pady=5)
        self.confidence_slider = tk.Scale(self, variable=self.confidence_var, from_=1, to=100, orient=tk.HORIZONTAL, length=198) # To match the length of the entry box, we are ocd
        self.confidence_slider.pack(padx=10, pady=5)
        tk.Label(self, text="How strong would the opponents bias be?").pack(padx=10, pady=5)
        self.strength_slider = tk.Scale(self, variable=self.strength_var, from_=1, to=100, orient=tk.HORIZONTAL, length=198)
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
        self.result = self.entry.get(), self.confidence_var.get() / 100 * self.strength_var.get() / 100
        self.close()

    def cancel(self):
        self.close()
        
    def close(self):
        del self.confidence_var
        del self.strength_var
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