import socket, sys, threading, pickle

class ThreadClient(threading.Thread):
    """
		dérivation d'un objet thread pour gérer la connexion avec un client
    """
	
    def __init__(self, conn):
        """
            Créer un nouvel objet thread pour gérer la connexion

            :param conn: connexion
            :type conn: string

            :return: Objet ThreadClient
            :rtype: ThreadClient
        """
        threading.Thread.__init__(self)
        self.connexion = conn
        
    def run(self):
        """
            Dialogue avec le client

            :return: None
            :rtype: NoneType
        """
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

