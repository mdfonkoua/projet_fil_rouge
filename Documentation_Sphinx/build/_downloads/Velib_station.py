from scipy.stats import norm
from time import time
import random    
import pandas as pd
import argparse
import os

host = '127.0.0.1'
port = 40000

import socket, sys, threading, pickle
from pygeocoder import Geocoder, GeocoderError
from time import time

class Station:
    def __init__(self, parameters, debug=False ):
        
        import random
        import time
        
        self.nom               = parameters[0]
        self.position          = parameters[1]
        self.nb_plot           = random.choice([10,15,20, 30]) # Nombre de places 
        self.nb_libre          = 0 # Nombre de places libres
        self.nb_velos          = self.nb_plot # On part du principe où toutes les places sont prises
        self.velos             = []     # Création d'une liste vide
        self.n_message         = -1 # ?
        self.debug             = False
        self.avaries           = [] # Avarie sur le vélo ?
        self.arrete            = False
        self.liste_d_avaries   = []
        self.nb_fois_en_arret  = 0
        self.logger_dispos     = logger("./../logs/stations_dispos.csv", header = "nom,n_message,time,nb_plot,nb_libre,nb_velos,lattitude, longitude")
        self.logger_reparation = logger("./../logs/stations_reparations.csv")
        self.logger_avarie     = logger("./../logs/stations_avarie.csv", header = "nom,n_message,time,avarie")
        
        self.log_dispo()
        nb_nom_velo=100
        noms = get_names(nb_nom_velo) # la définition de get_names est plus bas dans une autre cellule
        for n in range(self.nb_velos ):
            nom_velo= u"velo_"+"".join(["%s"%x for x in random.choice(noms)])
            self.velos.append(Velo(nom_velo , self))
        

    def log_reparation(self):
        self.log_dispo()
            
            
    def log_dispo(self):
        from time import time
        self.n_message = self.n_message + 1 # sachant qu'on commence à -1 donc on commence à 0
        dispo =(self.nom,self.n_message, time(),self.nb_plot, self.nb_libre, self.nb_velos,self.position[0][0], self.position[0][1])
        # On décrit la disponibilité de la station : le nom, combien de places libres...
        to_print = u"%s,%s,%s,%s,%s,%s,%s,%s"%dispo # On imprime le message résumant tout ce qui est en haut
        self.logger_dispos.log(to_print)
            
    def log_avarie(self, avarie):
        from time import time
        self.n_message = self.n_message + 1
        to_print = u"%s,%s,%s,%s"%(self.nom,self.n_message, time(), avarie) 
        
        self.logger_avarie.log(to_print)

    
    def avarie_possible(self):
        import math
        import random
        import time
        problemes   = { "plot"       : range(0, 20) , # Le nombre de places possibles
                       "half"        : range(20,30) , # ?
                       "network"     : range(30,35) , # problème de réseau
                       "electricite" : range(35,60) , 
                       "bug"         : range(60,90) } # bug de quelle nature ?
        zero     = 0
        mil      = 1000
        cent_mil = 100 * mil 
        
        for k,v in problemes.iteritems():
            if k in self.liste_d_avaries:
                r = random.randint(mil, cent_mil)
                new_range = range(r, r+30)
                problemes[k].extend(new_range)
        
        alea = random.randint(zero,cent_mil)
        avarie = False
        for k,v in problemes.iteritems():
            if alea in v:
                avarie = k
                
        if avarie:
            self.avaries.extend([avarie])
            if   avarie == "plot" : self.nb_libre = self.nb_libre -1 # Avarie sur une place
            elif avarie == "half" : self.nb_libre = math.floor(self.nb_libre - (self.nb_plot / float(2)))
            elif avarie == "bug"  : self.nb_libre = self.nb_libre - random.randint(0, self.nb_libre)
            elif avarie == "network" or avarie == "electricite": # Avarie sur toute la station
                self.nb_libre = 0
                self.arrete = True
                
            if self.nb_libre < 0: # On peut avoir un nombre de places libres inférieur à 0 ?
                self.nb_libre = 0            
            self.log_dispo()

            if avarie:
                self.log_avarie("%s"%avarie)
            
    def rendre_velo(self, velo, nb_km_trajet):
        import time
        self.avarie_possible()
        if self.nb_libre >0:
            self.velos.append(velo)
            velo.rendu(self, nb_km_trajet)
            self.nb_velos = len(self.velos)
            self.nb_libre = self.nb_libre - 1 # A chaque fois que je retourne un vélo, il enlève une place
            self.log_dispo()
            return 1 # Pour dire que j'ai un vélo disponible
        if 9500 < random.randint(0, 10000 ) :
            self.reparer() # ?
        return 0
    
    def reparer(self):
        self.nb_libre = self.nb_plot - self.nb_velos
        self.arrete   = False
        self.log_reparation()
        
    def prendre_velo(self):
        """
        retourne un vélo ou 0 en cas d'erreur.
        """
        import time
        self.avarie_possible()
        if self.velos and not self.arrete :
            to_return     = self.velos.pop()
            self.nb_velos = len(self.velos)
            self.nb_libre = self.nb_libre + 1
            self.log_dispo()
            return to_return
        
        if self.arrete:
            self.nb_fois_en_arret += 1 # erreur codage ?
        
        if self.nb_fois_en_arret > 10:
            self.reparer()

        return 0
    
    def get_nearest_station(self): # dans un carré ?
        x = self.position[0][0]
        y = self.position[0][1]
        deplacement_x = [-1, 0, 1]
        deplacement_y = [-1, 0, 1]
        deplacements  = [ (x_proche , y_proche) for x_proche in deplacement_x for y_proche in  deplacement_y if x_proche or y_proche]
        positions_proches = [(x +  a , y +  b) for a,b in  deplacements ]
        nearests = []
        for x2, y2 in positions_proches:
            if x2 + x < 0 or y2 + y < 0:
                continue 
            position_la_plus_proche = x2 * cote_len  + y2
            if 0 <= position_la_plus_proche and position_la_plus_proche < len(stations):
                nearests.append(stations[position_la_plus_proche])
        return nearests
        
                
    def __str__(self):
        return u"%s"%(self.nom)

class Velo:

    def __init__(self, nom, station):
        from scipy.stats import norm
        import time 
        performance            = norm( loc =0.9, scale=0.2 )
        
        self.nom               = "%s_%s"%(nom, time.time())
        self.performance       = performance.rvs(1)[0]
        self.station           = station
        self.degradation       = 0 # On part du principe qu'il n'y a pas de dégradation à l'initiale ?
        self.performances      = [] # A quoi ça sert ?
        self.debug             = True # False
        self.nb_km_trajet      = 0
        self.heures_rendu      = []
        self.disponible        = True
        self.logger_reparation = logger("./../logs/velo_reparations.csv", header = "velo,n_message,time,performance")
        self.logger_etat       = logger("./../logs/velos_etats.csv", header = "velo,n_message,time,station.nom,performance,nb_km_trajet")
                
        

        self.probleme_list     = self.get_problemes_list()
        self.n_message         = -1

    def get_problemes_list(self):
        """
        Créé le tableau de dégradations possible pour un vélo.
        """
        import math
        problemes       = [0] * int(math.ceil((50*self.performance)))
        problemes_bis   = {u"pedale" : 0.2, u"roue"  : 1 , u"degonfle" : 0.3, u"freins" : 0.05 , 0 : 0}
        problemes.extend(problemes_bis.values())
        return problemes
        
    def log_reparation(self):
        import time
        self.n_message = self.n_message + 1
        reparation     = (self.nom,self.n_message, time.time(),self.performance)
        to_print       = u"%s,%s, %s,%s"%reparation
        self.logger_reparation.log(to_print)
        

    def log_etat(self):
        from time import time
        self.n_message = self.n_message + 1
        to_print = u"%s,%s,%s,%s,%s,%s\n"%(   self.nom           ,
                                            self.n_message,
                                           time()            ,  
                                           self.station.nom  ,
                                           self.performance  ,
                                           self.nb_km_trajet )
        self.logger_etat.log(to_print)
    
    def rendu(self, station, nb_km_trajet):
        import time
        degradation       = random.choice(self.probleme_list)        
        self.disponible   = True
        self.performance  = self.performance - self.performance*degradation                                        
        self.nb_km_trajet = nb_km_trajet
        self.station      = station
        self.log_etat()
        if 900 < random.randint(0, 1000 ) :
            self.performance  = 1
            self.log_reparation()
        

    def __str__(self):
        return "%s"%self.nom

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

class ThreadReception(threading.Thread):
    """objet thread gérant la réception des messages"""
    def __init__(self, conn):
        threading.Thread.__init__(self)
        self.connexion = conn           # réf. du socket de connexion
        
    def run(self):
        while 1:
            message_recu = self.connexion.recv(1024).decode('utf-8')
            print("*" + message_recu + "*")
            if message_recu =='' or message_recu.upper() == "FIN":
                break
        # Le thread <réception> se termine ici.
        # On force la fermeture du thread <émission> :
        th_E._Thread__stop()
        print("Client arrêté. Connexion interrompue.")
        self.connexion.close()
    
class ThreadEmission(threading.Thread):
    """objet thread gérant l'émission des messages"""
    def __init__(self, conn):
        threading.Thread.__init__(self)
        self.connexion = conn           # réf. du socket de connexion
        
    def run(self):
        while 1:
            #message_emis = input()
            #message_emis = names[10]
            #self.connexion.sendall(message_emis.encode('utf-8'))
            message_emis = pickle.dumps(parameters)
            self.connexion.send(message_emis)
            th_E._Thread__stop()
            #message_emis_string = pickle.dumps(names)
            #self.connexion.send(message_emis_string)
        

def get_names(nb_noms):
    """
    retourne n mot de nb_lettres avec prefix.
    """
    import itertools
    from random import shuffle
    lettres = "azertyuiopqsdfghjklmwxcvbn1234567890"
    nb_lettres= 5
    prefix="Station_"
    names   = [] # pour initialiser ?
    for i in itertools.combinations(lettres, nb_lettres): # combinaisons possibles : 5 ** len(lettres)
        name = "".join(i)
        name = prefix + name
        names.append(name)
        #names = name
        nb_noms = nb_noms -1
        if nb_noms <2:
            break
    random.shuffle(names)
    return names


__version__ = '0.1.0'

NORTHERNMOST = 49.
SOUTHERNMOST = 25.
EASTERNMOST = -66.
WESTERNMOST = -124.

def coordinate_generator(number_of_points):
   
    coordinate_list = []
    counter = 0
    geocoder = Geocoder()

    while counter < number_of_points:
        lat = round(random.uniform(SOUTHERNMOST, NORTHERNMOST), 6)
        lng = round(random.uniform(EASTERNMOST, WESTERNMOST), 6)
        try:
            gcode = geocoder.reverse_geocode(lat, lng)

            if gcode[0].data[0]['formatted_address'][-6:] in ('Canada', 'Mexico'):
                continue
            elif 'unnamed road' in gcode[0].data[0]['formatted_address']:
                continue
            elif 'Unnamed Road' in gcode[0].data[0]['formatted_address']:
                continue
            else:
                counter += 1
                #coordinate_list.append((gcode[0].coordinates, gcode[0].formatted_address))
                coordinate_list.append(gcode[0].coordinates)
            # output_file.write(fullstring.format(gcode.x, gcode.y, gcode.address))
        except GeocoderError:
            continue
    print('Finished generating %d coordinate points' % counter)
    return coordinate_list

#Programme principal -------------------------------------------------------------------------------------------- 

import math
deplacement_x = [-1, 0, 1]
deplacement_y = [-1, 0, 1]
from time import time
import multiprocessing
#nb_cpu       = 2
nb_station   = 1
#debut        = time()
#process_pool = multiprocessing.Pool(nb_cpu)
#debut        = time()
nb_name      = 100
names        = get_names(nb_name)
cote_len     = int(math.ceil(math.sqrt(nb_station)))
positions    = coordinate_generator(1)
parameters   = [(names[10], positions)]

stations     = [Station(p) for p in parameters]
for x in stations:
    x.nearest = x.get_nearest_station()
nb_velos     = sum([len(station.velos) for station in stations])
#duree = time() - debut
#print ("duree = %s pour %s cree soit %s sec / unite"%(duree, nb_velos, duree/nb_velos))

#Établissement de la connexion :
connexion = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    connexion.connect((host, port))
except socket.error:
    print("La connexion a échoué.")
    sys.exit()    
print("Connexion établie avec le serveur.")
            
# Dialogue avec le serveur : on lance deux threads pour gérer
# indépendamment l'émission et la réception des messages :
th_E = ThreadEmission(connexion)
th_R = ThreadReception(connexion)
th_E.start()
th_R.start()        

