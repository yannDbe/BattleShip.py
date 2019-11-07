#!/usr/bin/python3
import socket
import select
import re

def main():
    joueur = {}
    s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM, 0)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.setsockopt(socket.SOL_TCP, socket.TCP_NODELAY, 1)
    s.bind(('',1234))
    s.listen(1)
    l = []
    while True:
        dispo, _, _ = select.select(l + [s], [], [])
        
        for ss in dispo:
            if ss == s:
                s2,addr = s.accept()
                l.append(s2)
                for user in l:
                    user.send(str(addr[0]).encode("utf-8") + b' JOINED THE GAME \r\n')
                    print('JOINED THE GAME\n')
            else:
                r = ss.recv(1024)
                if r == b'':
                    ss.close()
                    l.remove(ss)
                    for user in l:
                        user.send(b' LEFT THE GAME \r\n')
                elif r[0:7] != b'!addshot':
                    for user in l:
                        print(r)
                        if user != ss:
                            r = re.sub('!addshot ','',r.decode("utf-8"))
                            r = str.encode(r)
                            user.send(r)
                               
main()