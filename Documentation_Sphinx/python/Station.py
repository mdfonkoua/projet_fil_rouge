class Station:
    def __init__(self, parameters, debug=False ):
        """
            Créer un nouvel objet Station pour rentrer les paramètres d’une station

            :param parameters: parametres
            :type parameters: liste

            :param debug: debug
            :type debug: boolean

            :return: Objet Station
            :rtype: Station
        """        
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
        """
            Nombre de vélos en réparation

            :return: None
            :rtype: NoneType
        """
        self.log_dispo()
            
            
    def log_dispo(self):
        """
            Nombre de vélos disponibles

            :return: None
            :rtype: NoneType
        """
        from time import time
        self.n_message = self.n_message + 1 # sachant qu'on commence à -1 donc on commence à 0
        dispo =(self.nom,self.n_message, time(),self.nb_plot, self.nb_libre, self.nb_velos,self.position[0][0], self.position[0][1])
        # On décrit la disponibilité de la station : le nom, combien de places libres...
        to_print = u"%s,%s,%s,%s,%s,%s,%s,%s"%dispo # On imprime le message résumant tout ce qui est en haut
        self.logger_dispos.log(to_print)
            
    def log_avarie(self, avarie):
        """
            Avarie sur le vélo

            :return: None
            :rtype: NoneType
        """
        from time import time
        self.n_message = self.n_message + 1
        to_print = u"%s,%s,%s,%s"%(self.nom,self.n_message, time(), avarie) 
        
        self.logger_avarie.log(to_print)

    
    def avarie_possible(self):
        """
            problèmes potentiels sur le vélo

            :return: None
            :rtype: NoneType
        """
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
        """
            rendre un vélo sur une place disponible

            :return: None
            :rtype: NoneType
        """
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
        """
            reparer le velo

            :return: None
            :rtype: NoneType
        """
        self.nb_libre = self.nb_plot - self.nb_velos
        self.arrete   = False
        self.log_reparation()
        
    def prendre_velo(self):
        """
            prendre un vélo

            :return: un vélo ou 0 en cas d'erreur
            :rtype: int
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
