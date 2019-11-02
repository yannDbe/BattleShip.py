#!/usr/bin/python3
import socket
import select
import re

def main():
    nick = {}
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
                    user.send(str(addr[0]).encode("utf-8") + b' JOINED THE CHAT \r\n')
            else:
                r = ss.recv(1024)
                if r == b'':
                    ss.close()
                    l.remove(ss)
                    for user in l:
                        user.send(b' LEFT THE CHAT \r\n')
                elif r[0:4] == b'!msg':
                    for user in l:
                        if user != ss:
                            r = re.sub('!msg ','',r.decode("utf-8"))
                            r = str.encode(r)
                            user.send(b'> ' + r)
                elif r[0:4] == b'!nick':
                    nick[re.sub('!nick ','',r.decode("utf-8"))] = ss
                               
main()