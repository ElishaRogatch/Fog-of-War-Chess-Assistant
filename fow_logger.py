class FowLogger:
    def __init__(self):
        #with open("gamelog.txt", 'w') as logfile:
        #    logfile.write("")
        pass
    
    def log(self, message):
        with open("gamelog.txt", 'a') as logfile:
            print(message)
            print(message, file = logfile)
            
    def just_log(self, message):
        with open("gamelog.txt", 'a') as logfile:
            print(message, file = logfile)
            
    def clear_log():
        with open("gamelog.txt", 'w') as logfile:
            logfile.write("")