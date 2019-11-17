#!/usr/bin/python3
import socket
import select
import re
from game import *
import pickle

#Crée une grille de jeu aléatoire pour chaque joueur
def randomConfiguration():
    boats = []
    #Vérifie la configuration de la grille (Les bateaux ne doivent pas se superposer)
    while not isValidConfiguration(boats):
        boats=[]
        for i in range(5):
            x = random.randint(1,10)
            y = random.randint(1,10)
            isHorizontal = random.randint(0,1) == 0
            boats = boats + [Boat(x,y,LENGTHS_REQUIRED[i],isHorizontal)]
    #Retourne une configuraton valide
    return boats

def main():
    boats1 = randomConfiguration() #Crée la matrice du joueur 1
    boats2 = randomConfiguration() #Crée la matrice du joueur 2

    #Création de la partie réseau qui permet de se connecter au serveur
    s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM, 0)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.setsockopt(socket.SOL_TCP, socket.TCP_NODELAY, 1)
    s.bind(('',1234)) #Port du socket
    s.listen(1)
    l = []
    JoueurUn = False

    while True:
        dispo, _, _ = select.select(l + [s], [], [])

        for ss in dispo:
            if ss == s:
                #Accepte la connexion sur la socket
                s2,addr = s.accept()
                l.append(s2) #Ajoute la connexon dans une liste
                adresse = (str(addr).encode("utf-8"))
                print('%s JOINED THE GAME' % adresse)
                if len(l) == 2: #Quand 2 joueurs on rejoint le serveur, la partie démarre
                    for user in l:
                        user.send(b'!start')

            else:
                r = ss.recv(1024)
                if r == b'': #Si le serveur reçoit un message vide alors il ferme la connexion (joueur parti)
                    ss.close()
                    l.remove(ss) #Enlève la socket du joueur de la liste pour pouvoir la réutiliser
                    for user in l:
                        user.send(b' LEFT THE GAME \r\n') #Annonce que l'autre joueur à quitté
                if r[0:8] == b'!addshot': #Boucle activé à chaque fois qu'un joueur réalise un coup
                    for user in l:
                        if user != ss:
                            user.send(r)
                if r[0:7] == b'!whoami': #Le premier client à envoyer la commande est le premier joueur
                    if JoueurUn == False:
                        ss.send(b'!whoami 0')
                        JoueurUn = True
                    elif JoueurUn == True:
                        ss.send(b'!whoami 1')
                if r[0:7] == b'!boats1': #Envoie la matrice à jour
                    boats1_data = pickle.dumps(boats1)
                    ss.send(boats1_data)
                if r[0:7] == b'!boats2':
                    boats2_data = pickle.dumps(boats2)
                    ss.send(boats2_data)

main()
