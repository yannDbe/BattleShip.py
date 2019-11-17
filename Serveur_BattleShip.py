#!/usr/bin/python3
import socket
import select
import re

def main():
    s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM, 0)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.setsockopt(socket.SOL_TCP, socket.TCP_NODELAY, 1)
    s.bind(('',1234))
    s.listen(1)
    l = []
    JoueurUn = False
    while True:
        dispo, _, _ = select.select(l + [s], [], [])
        
        for ss in dispo:
            if ss == s:
                s2,addr = s.accept()
                l.append(s2)
                adresse = (str(addr).encode("utf-8"))
                print('%s JOINED THE GAME' % adresse)
                if len(l) == 2:
                    for user in l:
                        user.send(b'!start')
                    
            else:
                r = ss.recv(1024)
                if r == b'':
                    ss.close()
                    l.remove(ss)
                    for user in l:
                        user.send(b' LEFT THE GAME \r\n')
                if r[0:8] == b'!addshot':
                    for user in l:
                        if user != ss:
                            user.send(r)
                if r[0:7] == b'!whoami':
                    if JoueurUn == False:
                        ss.send(b'!whoami 0')
                        JoueurUn = True
                    elif JoueurUn == True:
                        ss.send(b'!whoami 1')

main()