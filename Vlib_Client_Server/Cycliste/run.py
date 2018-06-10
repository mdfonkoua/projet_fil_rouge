#! /usr/bin/python
from scipy.stats import norm
from time import time
import random    
import pandas as pd
import argparse
import os

host = 'server'
port = 40000

import socket, sys, threading, pickle
from pygeocoder import Geocoder, GeocoderError
from time import time

class Cycliste:

    def __init__(self, parameters):
        import time
        import random
        from scipy.stats import norm
        import random
        
        """ ==========================================================
                                    Variables
        ==============================================================="""
        
        homme   = "homme"
        femme   = "femme"
        age_min = 14 
        age_max = 80
        sexe    = random.choice([homme, femme]) # choisit un élément aléatoire dans une liste
        age     = random.randint(age_min ,age_max)
        sportif = random.choice([-0.5, 0, 2, 4, 6 ]) 
        
        # Les chiffres qui vont suivre en paramètre ont été choisis au hasard comme référence
        
        if   age < 35 : facteur = norm( loc =1.2, scale=0.2 ) 
        elif age < 50 : facteur = norm( loc =1  , scale=0.2 )
        elif age < 90 : facteur = norm( loc =0.7, scale=0.2 )

        if sexe == homme:
            vitesse_de_base  = 20
            nb_km            = norm( loc =7, scale=4 )
        else:
            vitesse_de_base  = 15
            nb_km            = norm( loc =10, scale=4 )
        vitesse_moyenne      = vitesse_de_base * facteur.rvs(1) + sportif # rvs nous permet de choisir au hasard dans la variable facteur
        
        """ ==========================================================
                                    Attributs
        ==============================================================="""
        #self.identifiant     = "cycliste_%s"%parameters[0]
        self.identifiant     = parameters[0] 
        self.station_maison  = parameters[1]
        #self.station_travail = parameters[2]
        self.station_travail = ""
        self.sportif         = sportif
        self.age             = age
        self.sexe            = sexe
        self.nb_km           = nb_km.rvs(1)[0]
        self.vitesse         = vitesse_moyenne[0]
        self.sur_velo        = False
        self.debug           = False
        self.nb_trajet       = 0
        self.durees          = []
        self.trajets         = []
        self.velo            = False
        self.prises          = []
        self.attente         = 0.5 ; #random.randint(0,10)
        self.last_rendu      = time.time()
        self.logger_cycliste = logger("./../logs/cycliste_cyclistes.csv", 0, header = "cycliste,sportif,age,sexe,nb_km,vitesse,attente"        )
        self.logger_prise    = logger("./../logs/cycliste_prises.csv", header = "cycliste,heure_de_depart,velo,action")
        self.logger_rendu    = logger("./../logs/cycliste_rendu.csv", header = "cycliste,heure_de_depart,heure_d_arrivee,nb_km_trajet,velo.nom")
        self.logger_debug    = logger("./../logs/cycliste_debug.csv",1, header = "cycliste,n_message,time,message")
        
        
        
        
        self.a_la_maison     = True
        self.n_message       = 0
        self.trajet_courant  = ""
        
        """ ==========================================================
                                    Logs
        ==============================================================="""        
        self.log_cycliste()
        self.logger_debug.log("cree")        
        self.log_debug(u"station_maison = %s"%self.station_maison)
        self.log_debug(u"station_travail = %s"%self.station_travail)
        #self.log_debug(u"station_maison nearest= %s"%"|".join([x.nom for x in self.station_maison.nearest]))
        #self.log_debug(u"station_travail nearest= %s"%"|".join([x.nom for x in self.station_travail.nearest]))
        
    def peut_prendre_velo(self, station):
        """
        Renvoie un velo ou bien False.
        """
        from time import time
        import random
        
        """ __________________________________________________________
                            Préconditions
        ______________________________________________________________"""        
        if time() < self.attente + self.last_rendu: 
            self.log_debug(u"trop t ") # attente : temps de travail + heure du dernier rendu du vélo au travail
        if self.sur_velo:
            self.log_debug(u"en route")
            return False, False # Est ce que je peux avoir les 2 ? Trop tot et en route ?
        
        """ __________________________________________________________
                    Recherche de vélo sur les stations proches
        ______________________________________________________________"""        
        random.shuffle(station.nearest) # le nearest est calculé en fonction du lieu de travail et d'habitation ?
        for local_station in station.nearest:
            velo = local_station.prendre_velo()            
            if not velo: 
                self.log_debug(u"pas de velo sur la station %s " % local_station)
                continue
            if local_station in self.station_maison.nearest : elem_de = "station maison"
            else                                            : elem_de = "station travail"
            self.log_debug(u"velo pris sur station %s (elem de %s)" % (local_station,elem_de))
            return velo , local_station
        
        """ __________________________________________________________
                                    Aucun vélo trouvé
        ______________________________________________________________"""        
        self.log_debug(u"Aucun velo trouve aux alentours.")
        return False, False
    
    
    def prend_velo(self):
        import time
        
        if   self.a_la_maison : station = self.station_maison
        else                  : station = self.station_travail
        
        velo, station = self.peut_prendre_velo(station)
        if not velo :
            return 
                       
        self.log_debug(u"%s a pris le velo %s sur la station %s"%(self.a_la_maison, velo, station))
        velo.disponible      = False
        self.sur_velo        = True
        self.heure_de_depart = time.time()
        self.velo            = velo
        self.trajet_courant  = trajet(self, velo,station)
        self.log_prise()
        try:
            nb_km_local          = norm( loc =self.nb_km, scale=self.nb_km/float(3) ).rvs(1)[0] 
        except Exception as e:
            self.log_debug(u"pbm sur nb_km_local = self.nb_km = %s " %self.nb_km)
            nb_km_local = 15
        try:
            vitesse_local        = norm(loc = self.vitesse, scale = self.vitesse/float(10)).rvs(1)[0]
            vitesse_local        = vitesse_local * velo.performance
        except:
            self.log_debug(u"pbm sur vitesse_local self.vitesse = %s"%self.vitesse)
            vitesse_local = self.vitesse
            
        self.nb_km_trajet    = nb_km_local
        duree                = nb_km_local / vitesse_local
        self.heure_d_arrivee = self.heure_de_depart + duree
        
        if velo.performance < 0.1:
            duree                = 0
            #self.durees.append( duree)
            self.heure_d_arrivee =  self.heure_de_depart # il n'est pas parti. Est ce qu'on part du principe que le vélo
            self.nb_km_trajet    = 0 # a été attribué et qu'il n'a pas bougé ou tout simplement qu'on ne l'a pas attribué
            self.log_debug(u"velo defaillant < 0.1, rendu a la meme station :-( ")
            self.rendre_vite_velo(station)
            return
        
        self.a_la_maison = not self.a_la_maison
        
        if velo.performance < 0.3: # Est ce qu'on part du principe qu'il n'est plus dans la station de la maison ?
            duree                = duree / 10 # sinon un intervalle (entre 0.1 et 0.3). Durée calculée en minutes ?
            #self.durees.append( duree)
            self.heure_d_arrivee =  self.heure_de_depart + duree
            self.nb_km_trajet    = self.nb_km_trajet / float(10)
            self.log_debug(u"velo defaillant <0.3, rendu a la meme station :-( ")
            self.rendre_vite_velo(station)
            
        elif velo.performance < 0.5:
            duree                = duree * 1.5
            #self.durees.append( duree)
            self.nb_km_trajet    = self.nb_km_trajet 
            self.heure_d_arrivee =  self.heure_de_depart + duree 
            self.log_debug(u"velo defaillant <0.5")
        else:
            pass
            #self.durees.append( duree)




    def rendre_vite_velo(self, station):        
        import time
        
        if not self.sur_velo:
            self.log_debug(u"pas en chemin")    
            return 0
        
        if time.time() < self.heure_d_arrivee: # si le vélo n'est pas encore arrivé, comment on peut avoir heure d'arrivée pour comparer ?
            self.log_debug(u"pas encore arrive")
            return
        
        if self.a_la_maison:
            station = self.station_maison
            elem_de = "station_maison"
        else:
            station = self.station_travail
            elem_de = "station_travail"
        self.log_debug(u"self.a_la_maison = %s"%self.a_la_maison)    
        
        rendu = False
        
        for local_station in station.nearest:
            if local_station.rendre_velo(self.velo, self.nb_km_trajet):
                self.log_debug(u"velo rendu sur la station %s ( a la maison = %s) (elem de %s)"%(local_station, self.a_la_maison, elem_de))    
                rendu = True
                break
            else:
                self.log_debug(u"impossible de rendre sur ,%s ( a la maison = %s)"%(local_station, self.a_la_maison))    
        if not rendu:
            return
                        
        self.last_rendu = time.time()
        duree_constatee = self.last_rendu - self.heure_de_depart
        trajet          = (self.heure_de_depart, self.heure_d_arrivee, self.identifiant, self.nb_km_trajet, self.velo.nom )
        self.sur_velo  = False
        self.nb_trajet = self.nb_trajet + 1
        self.log_rendu()
        self.trajet_courant.fin(local_station)
        self.velo      = False
        
        #self.trajets.append(trajet)
    def rendre_velo(self):        
        import time
        
        if not self.sur_velo:
            self.log_debug(u"pas en chemin")    
            return 0
        
        if time.time() < self.heure_d_arrivee:
            self.log_debug(u"pas encore arrive")
            return
        
        if self.a_la_maison:
            station = self.station_maison
            elem_de = "station_maison"
        else:
            station = self.station_travail
            elem_de = "station_travail"
        self.log_debug(u"self.a_la_maison = %s"%self.a_la_maison)    
        
        rendu = False
        for local_station in station.nearest:
            if local_station.rendre_velo(self.velo, self.nb_km_trajet):
                self.log_debug(u"velo rendu sur la station %s (a la maison = %s) (elem de %s)"%(local_station, self.a_la_maison, elem_de))    
                rendu = True
                break
            else:
                self.log_debug(u"impossible de rendre sur ,%s (a la maison = %s)"%(local_station, self.a_la_maison))    
        if not rendu:
            return
                        
        self.last_rendu = time.time()
        duree_constatee = self.last_rendu - self.heure_de_depart
        trajet          = (self.heure_de_depart, self.heure_d_arrivee, self.identifiant, self.nb_km_trajet, self.velo.nom )
        self.sur_velo  = False
        self.nb_trajet = self.nb_trajet + 1
        self.log_rendu()
        self.trajet_courant.fin(local_station)
        self.velo      = False
        
        #self.trajets.append(trajet)

    def get_nearest_station(self, cycliste): # dans un carré ?
        import csv
        import math
        position = cycliste[0][1]
        with open("./../logs/stations_dispos.csv") as f:
            reader = csv.reader(f)
            nearests = []
            resultat = []
            for nom,n_message,time,nb_plot,nb_libre,nb_velos,lattitude, longitude in reader:
                # The csv module already extracts the information for you
                #print (nom,n_message,time,nb_plot,nb_libre,nb_velos,lattitude, longitude)
                if (nom != "nom"):
                    xA = float(lattitude)
                    yA = float(longitude)
                    xB = float(position[0][0])
                    yB = float(position[0][1])
                    distance = math.sqrt((xB - xA)**2 + (yB - yA)**2)
                    #print("Bonjour, la distance qui sépare les deux points est de " + str(distance))
                    nearests.append(nom)
                    resultat.append(distance)
        #x = self.position[0][0]
        #y = self.position[0][1]
        #deplacement_x = [-1, 0, 1]
        #deplacement_y = [-1, 0, 1]
        #deplacements  = [ (x_proche , y_proche) for x_proche in deplacement_x for y_proche in  deplacement_y if x_proche or y_proche]
        #positions_proches = [(x +  a , y +  b) for a,b in  deplacements ]
        #nearests = []
        #for x2, y2 in positions_proches:
        #    if x2 + x < 0 or y2 + y < 0:
        #        continue 
        #    position_la_plus_proche = x2 * cote_len  + y2
        #    if 0 <= position_la_plus_proche and position_la_plus_proche < len(stations):
        return nearests, resultat        
            
    def __str__(self):
        return self.identifiant
    
    def log_cycliste(self):

        to_print = u"%s,%s,%s,%s,%s,%s,%s"%(    self.identifiant   ,self.sportif     ,
                                                 self.age         ,self.sexe        ,
                                                 self.nb_km       ,self.vitesse     , self.attente )
        
        self.logger_cycliste.log(to_print)
            
    def log_prise(self, action="prise"):

        to_print = u"%s,%s,%s,%s"%( self.identifiant,self.heure_de_depart, self.velo.nom, action)
        self.logger_prise.log(to_print)
            
    def log_rendu(self, action="rendu"):

        to_print = u"%s,%s,%s,%s,%s\\n"%( self.identifiant, self.heure_de_depart, 
                                       self.heure_d_arrivee,  self.nb_km_trajet, self.velo.nom )

        self.logger_rendu.log(to_print)
        
    def log_debug(self, message):
        from time import time
        to_print = u"%s,%04d, %s,%s"% (self.identifiant,self.n_message, time() , message)
        self.n_message = self.n_message + 1
        self.logger_debug.log(to_print)



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
            message_emis = input()
            #message_emis = names[10]
            self.connexion.sendall(message_emis.encode('utf-8'))
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
    prefix="Cycliste_"
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
cyclistes     = [Cycliste(p) for p in parameters]

#print (cyclistes)
values = []
for x in cyclistes:
	x.nearest,values = x.get_nearest_station(parameters)
numero_index     = values.index(min(values))
#duree = time() - debut
print ("Vous etes bien connecté à la plateforme V")
print ("station la plus proche = %s à une distance %s "%(x.nearest[numero_index], values[numero_index]))

#Établissement de la connexion :
connexion = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    connexion.connect((host, port))
    message_emis = pickle.dumps(parameters)
    connexion.send(message_emis)
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

