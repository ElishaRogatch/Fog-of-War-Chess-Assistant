import tkinter as tk 

class MessageOutput(tk.Toplevel):
    """Display a popup telling the user a message"""
    def __init__(
        self, 
        parent, 
        message, 
        title = "", 
        icon_path=None, 
        wrap_length=0, 
        label_font="TkDefaultFont",
        min_size = (200, 150),
        label_padding = (10,5)
    ):
        super().__init__(parent)
        self.parent = parent
        self.iconbitmap(icon_path)
        self.protocol("WM_DELETE_WINDOW", self.close)
        self.minsize(min_size[0], min_size[1])
        self.title(title)
        
        # Makes this popup window behave like a dependent child of the parent
        self.transient(parent)
        # Grabs the focus and puts it onto this child window
        self.grab_set()

        tk.Label(self, text=message, wraplength=wrap_length, font=label_font).pack(padx=label_padding[0], pady=label_padding[1])

        # OK button
        tk.Button(self, text="OK", command=self.ok).pack(side=tk.BOTTOM, padx=10, pady=5)

        # Pauses code until answered
        self.wait_window(self)


    def ok(self):
        self.close()
        
    def close(self):
        self.destroy()
        
class YesNoIO(tk.Toplevel):
    """Display a popup asking the user a yes/no quesion"""
    def __init__(self, parent, question, title = "", icon_path=None):
        super().__init__(parent)
        self.parent = parent
        if icon_path is not None:
            self.iconbitmap(icon_path)
        self.protocol("WM_DELETE_WINDOW", self.no)
        self.title(title)
        self.result = False
        
        # Makes this popup window behave like a dependent child of the parent
        self.transient(parent)
        # Grabs the focus and puts it onto this child window
        self.grab_set()

        tk.Label(self, text=question).pack(padx=30, pady=15)

        # Yes and No buttons
        button_frame = tk.Frame(self)
        tk.Button(button_frame, text="Yes", command=self.yes).pack(side=tk.LEFT, padx=10, pady=5)
        tk.Button(button_frame, text="No", command=self.no).pack(side=tk.RIGHT, padx=10, pady=5)
        button_frame.pack(padx=10, pady=15)

        # Pauses code until answered
        self.wait_window(self)


    def yes(self):
        # Store the true result
        self.result = True
        self.close()

    def no(self):
        self.close() # Result is already False by default
        
    def close(self):
        self.destroy()