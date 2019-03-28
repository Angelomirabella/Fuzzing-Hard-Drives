import sys
from boofuzz import *

def main():

    if len(sys.argv) != 3:
        print "Usage: python fuzzer.py <port> <iterations>"
        exit(0)


    session = Session(target=Target(connection=SocketConnection("127.0.0.1", int(sys.argv[1]), proto='tcp')))

    s_initialize("opcode")
    s_byte(0xa1,fuzzable=False) #not fuzzable

#    protocol
#    s_byte(0xc,full_range=True) #not fuzzable 6<<1  / 4<<1

 #  flags
#    s_byte(0x2e,full_range=True) #not fuzzable

#    s_byte(0x0,full_range=True) #features

#    s_byte(0x0,full_range=True) #sector_count

  # lba_low
#    s_byte(0x0,full_range=True)

#   lba_mid
#    s_byte(0x0,full_range=True)

 #  lba_high
#    s_byte(0x0,full_range=True)


#   device
#    s_byte(0x40,full_range=True)

    #command
#    s_byte(0x25,full_range=True)
#
    #reserved
#    s_byte(0x0,full_range=True)

    #control
#    s_byte(0,full_range=True)

#    s_byte(0xc2e000000000040250000)
    s_random(0x0c2e000000000040250000,11,11,int(sys.argv[2]))


    s_static("\n")

    session.connect(s_get("opcode"))



    session.fuzz()

if __name__ == "__main__":
    main()

