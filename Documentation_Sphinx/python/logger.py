class logger(): ## A quoi sert la classe
    """
    Save data into memory (in an array) and write it down to a file after [nb_log] is reached.
    """
    def __init__(self, path, limit_to_save_to_disk=1, header=None): # Définition du constructeur
        import os.path
        self.path    = path # On crée une variable self.path et on lui donne comme valeur path
        self.limit   = limit_to_save_to_disk 
        self.logs    = [] ## Pour rentrer le log ? Qu'est ce que le log
        self.nb_logs = 0
        if header:
            if not os.path.isfile(path):
                with open(path, "a") as f:
                    f.write(header)
                    f.write("\n")
        
    def log(self, string):
        self.logs.append(string)
        self.nb_logs = self.nb_logs +1
        if self.limit <= self.nb_logs:
            self.write_to_disk()
    
    def write_to_disk(self):
        from time import time
        heure = time()
        new_path = "%s_%s.csv"%(self.path, heure)
        new_path = self.path
        with open(new_path, "a") as f:
            while len(self.logs):
                try:
                    a = self.logs.pop()
                    f.write(u"%s\n"%a)
                except:
                    print ("pbm d'encodage avec la phrase :  ") 
                    print (a)
        self.nb_logs = len(self.logs)
    def __del__(self):
        self.write_to_disk()
