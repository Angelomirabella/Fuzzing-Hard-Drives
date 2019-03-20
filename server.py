import socket
import ata
import sys
from boofuzz import *


s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.bind(('',int(sys.argv[1])))
fs=s.makefile('rw',0)
s.listen(1)

print 'Waiting Connections...'

while True:
    client_s, addr= s.accept()
    fs=client_s.makefile('rw',0)
    print 'Connection from ', addr

    data=fs.readline()
    for i in data:
        print hex(ord(i))
    #print data
    
