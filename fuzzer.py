import sys
from boofuzz import *

def main():
    session = Session(target=Target(connection=SocketConnection("127.0.0.1", int(sys.argv[1]), proto='tcp')))

    s_initialize("opcode")
    s_byte(0xa1) #not fuzzable
#    s_static("\n")

#    s_initialize("protocol")
    s_bit_field(0b00001100,8,name='protocol') #not fuzzable 6<<1  / 4<<1
#    s_static("\n")

 #   s_initialize("flags")
    s_byte(0x2e) #not fuzzable
#    s_static("\n")
  
    s_byte(0x0) #features

    s_byte(0x0) #sector_count 

  #  s_initialize("lba_low")
    s_byte(0x0) 
#    s_static("\n")

   # s_initialize("lba_mid")
    s_byte(0x0)
#    s_static("\n")

    #s_initialize("lba_high")
    s_byte(0x0)
#    s_static("\n")

   # s_initialize("device")
    s_byte(0x40)
#    s_static("\n")

    #s_initialize("command")
    s_byte(0x25)
#    s_static("\n")

    #s_initialize("reserved")
    s_byte(0x0)
#    s_static("\n")

    #s_initialize("control")
    s_byte(0)

    s_static("\n")

    session.connect(s_get("opcode"))
    #session.connect(s_get("opcode"), s_get("protocol"))
    #session.connect(s_get("protocol"), s_get("flags"))
    #session.connect(s_get("flags"), s_get("lba_low"))
    #session.connect(s_get("lba_low"), s_get("lba_mid"))
    #session.connect(s_get("lba_mid"), s_get("lba_high"))
    #session.connect(s_get("lba_high"), s_get("device"))
    #session.connect(s_get("device"), s_get("command"))
    #session.connect(s_get("command"), s_get("reserved"))
    #session.connect(s_get("reserved"), s_get("control"))
    session.fuzz()

if __name__ == "__main__":
    main()

