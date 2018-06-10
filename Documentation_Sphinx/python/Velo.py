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
		