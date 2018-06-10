Aide
====

Ceci est l'aide de la documentation.
Vous trouvez ici une FAQ concernant le projet.

1. Comment compiler la documentation ?

.. code-block:: bash

  sphinx-build -b html ./source ./build

2. Comment lancer le client-serveur via docker...

voici les commandes à éxécuter dans l'ordre:

-se placer dans le dossier "Vlib_Client_Server"

-ouvrir une console et lancer la commande:

.. code-block:: bash

  docker-compose up --build

-attendre que les 3 images "server", "station" et "cycliste" soient créées à la fin de la commande précèdente

-ouvrir une autre console et lancer la commande:

.. code-block:: bash

  docker exec -it server /bin/bash

-attendre la fin d'exécution de la commande précedente et voir si la console vous donne la main dans la machine server à partir du répertoire /

-lancer la commande:

.. code-block:: bash

  python run.py
  
-et le message "serveur en attente de connexion..." s'affiche

-ouvrir une autre console et lancer la commande:

.. code-block:: bash

  docker exec -it station /bin/bash

-attendre la fin d'exécution de la commande précedente et voir si la console vous donne la main dans la machine station à partir du répertoire /app

-lancer la commande:

.. code-block:: bash

  python run.py
  
-et le message "connexion établie avec succès..." s'affiche

-ouvrir une autre console et lancer la commande:

.. code-block:: bash

  docker exec -it cycliste /bin/bash"

-attendre la fin d'exécution de la commande précedente et voir si la console nous donne la main dans la machine cycliste à partir du répertoire /app. 

-lancer la commande:

.. code-block:: bash

  python run.py
  
-et le message "connexion établie avec succès.." s'affiche avec la station la plus proche.