import socket
import select
import threading
import select

l=[]
NICK = {}
s = None

def boucleSocket(sock, msg):
    for i in l:
        if i == s or i == sock:
            pass
        else:
            i.send(msg)

def main():
    global s
    global i
    s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM, 0)
    #réutilisation du port
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    #désac algo Nagle
    s.setsockopt(socket.SOL_TCP, socket.TCP_NODELAY, 1)

    s.bind(('', 7777)) #Sélection du port
    s.listen(1) #écoute active
    l.append(s) #Ajout du socket dans la liste l

    while True:
            readl, writel, errorl = select.select(l, [], [])
            for sock in readl:
                #Envoi
                if sock == s:
                    s3,addr = s.accept()
                    l.append(s3)
                    adresse = (str(addr).encode("utf-8"))
                    NICK[s3] = (adresse,"")
                    boucleSocket(s3,b"%s vient de rejoindre le chat\n" % adresse) #Message affiché quand quelqu'un rejoin le chat
                    print("LE DICO\n \n", str(NICK))

                    s3.send(b"JOIN\n") #Affiche JOIN
                #Réception
                else:
                    r = sock.recv(1500) #Message reçu

                    boucleSocket(sock, r)
                    if r == b'':
                        boucleSocket(sock,b"%s vient de quitter le chat\n" % (str(addr).encode("utf-8")))
                        boucleSocket(sock,b"PART\n")
                        sock.close()
                        l.remove(sock)

###############################LIST OF COMMANDS##########################################
                    if r == b'/NICK\n': #Si message = /NICK
                        sock.send(b"Nom : ")
                        NICK[sock] = (NICK[sock][0],sock.recv(1500))
                        sock.send(b"%s s'appelle maintenant : %s \n" % (str(addr).encode("utf-8"), NICK[sock][1]))
                        print("LE DICO\n \n", str(NICK))

                    if r == b'/LIST\n':
                        sock.send(b"Liste des connectes : \n")
                        for adresse, nom in NICK.values():
                            sock.send(nom)

########################################################################################


main()
