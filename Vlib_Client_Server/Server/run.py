#! /usr/bin/python
# coding: utf-8

# In[ ]:


# Définition d'un serveur réseau gérant un système de CHAT simplifié.
# Utilise les threads pour gérer les connexions clientes en parallèle.
HOST = '0.0.0.0'
PORT = 40000

import socket, sys, threading, pickle

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
 
class ThreadClient(threading.Thread):
    '''dérivation d'un objet thread pour gérer la connexion avec un client'''
    def __init__(self, conn):
        threading.Thread.__init__(self)
        self.connexion = conn
        
    def run(self):
        # Dialogue avec le client :
        nom = self.getName()        # Chaque thread possède un nom
        while 1:
            msgClient = self.connexion.recv(1024)
            msgClient_list = pickle.loads(msgClient)
            if msgClient.upper() == "FIN" or msgClient =="":
                break
            message = "%s> %s connectée; Position : %s" % (nom, msgClient_list[0][0].upper(), msgClient_list[0][1])
            """log =(msgClient_list[0][0].upper(),adresse[0],self.position[0][0], self.position[0][1])
            to_print = u"%s,%s,%s,%s"%log # On imprime le message résumant tout ce qui est en haut
            self.logger_server.log(to_print)"""
            print(message)
            # Faire suivre le message à tous les autres clients :
            #for cle in conn_client:
            #    if cle != nom:      # ne pas le renvoyer à l'émetteur
            #        conn_client[cle].sendall(message.encode('utf-8'))
                    
        # Fermeture de la connexion :
        self.connexion.close()      # couper la connexion côté serveur
        del conn_client[nom]        # supprimer son entrée dans le dictionnaire
        print("Client %s déconnecté." % nom)
        # Le thread se termine ici    

# Initialisation du serveur - Mise en place du socket :
mySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    mySocket.bind((HOST, PORT))
except socket.error:
    print("La liaison du socket à l'adresse choisie a échoué.")
    sys.exit()
print("Serveur Velib prêt, en attente de connexions ...")
mySocket.listen(5)

#logger_server = logger("./../logs/serveur_client.csv", header = "nom_station,ip,lattitude, longitude")

# Attente et prise en charge des connexions demandées par les clients :
conn_client = {}                # dictionnaire des connexions clients
while 1:    
    connexion, adresse = mySocket.accept()
    # Créer un nouvel objet thread pour gérer la connexion :
    th = ThreadClient(connexion)
    th.start()
    # Mémoriser la connexion dans le dictionnaire : 
    it = th.getName()        # identifiant du thread
    conn_client[it] = connexion
    
    print("Client %s connecté, adresse IP %s, port %s." %(it, adresse[0], adresse[1]))
    # Dialogue avec le client :
    #connexion.sendall("Connexion reussie avec le serveur Velib".encode('utf-8'))

    

