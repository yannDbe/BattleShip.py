#!/usr/bin/python3

from game import *
import socket
import random
import time
import re
import pickle

hostname = 'localhost'
port = 1234

#Affiche la confiuration du joueur
def displayConfiguration(boats, shots=[], showBoats=True):
    Matrix = [[" " for x in range(WIDTH+1)] for y in range(WIDTH+1)]
    for i  in range(1,WIDTH+1):
        Matrix[i][0] = chr(ord("A")+i-1)
        Matrix[0][i] = i

    if showBoats:
        for i in range(NB_BOATS):
            b = boats[i]
            (w,h) = boat2rec(b)
            for dx in range(w):
                for dy in range(h):
                    Matrix[b.x+dx][b.y+dy] = str(i)
    #Affiche un X si la cible est touchée ou un O si le tir est raté
    for (x,y,stike) in shots:
        if stike:
            Matrix[x][y] = "X"
        else:
            Matrix[x][y] = "O"


    for y in range(0, WIDTH+1):
        if y == 0:
            l = "  "
        else:
            l = str(y)
            if y < 10:
                l = l + " "
        for x in range(1,WIDTH+1):
            l = l + str(Matrix[x][y]) + " "
        print(l)

""" display the game viewer by the player"""
def displayGame(game, player):
    global otherPlayer
    otherPlayer = (player+1)%2
    displayConfiguration(game.boats[player], game.shots[otherPlayer], showBoats=True)
    displayConfiguration([], game.shots[player], showBoats=False)

def main():
    sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    sock.connect((hostname,port))

    print("Attente d'un(e) autre joueur(se)")
    while True:
        r = sock.recv(1024)
        if r[0:6] == b'!start':
            print("C'est partie")
            break

    sock.send(b'!whoami')

    while True:
        r = sock.recv(1024)
        if r[0:7] == b'!whoami':
            r = re.sub('!whoami ','',r.decode("utf-8"))
            currentPlayer = int(r)
            me = int(r)
            break

    sock.send(b'!boats1')

    while True:
        r = sock.recv(4096)
        if r != b'':
            boats1 = pickle.loads(r)
            break

    sock.send(b'!boats2')

    while True:
        r = sock.recv(4096)
        if r != b'':
            boats2 = pickle.loads(r)
            break

    game = Game(boats1, boats2)
    displayGame(game, me)

    while gameOver(game) == -1:
        #Attend un imput des coordonnées
        if currentPlayer == J0:
            x_char = input ("quelle colonne (J%s) ? " %me)
            x_char.capitalize()
            x = ord(x_char)-ord("A")+1
            y = int(input ("quelle ligne (J%s) ? " %me))
            coordonne = "!addshot x: " + str(x) + " y: " + str(y)
            sock.send(str(coordonne).encode('utf-8')) #Envoi les coordonnées du tir au serveur

        elif currentPlayer == J1:
            while True:
                r = sock.recv(1024)
                if r[0:8] == b'!addshot':
                    r = r.decode()
                    x = int(r[12])
                    y = int(r[17])
                    break

        addShot(game, x, y, otherPlayer)
        print("======================")
        displayGame(game, me)
        currentPlayer = (currentPlayer+1)%2
    print("game over")
    print("your grid :")
    displayGame(game, J0)
    print("the other grid :")
    displayGame(game, J1)

    if gameOver(game) == J0:
        print("You win !")
    else:
        print("you loose !")

main()
