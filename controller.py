import sys
import vm
from boofuzz import *

def main():

    if len(sys.argv) != 3:
        print "Usage: sudo  python controller.py <port> <iterations>"
        exit(0)


    session = Session(target=Target(connection=SocketConnection("127.0.0.1", int(sys.argv[1]), proto='tcp')))

    s_initialize("ata_pass_through")
    s_byte(0xa1,fuzzable=False) #not fuzzable
    s_byte(0xc,fuzzable=False) #not fuzzable 6<<1  / 4<<1
    s_byte(0x2e,fuzzable=False)
    s_random(0x000000000040250000,9,9,int(sys.argv[2]))


    s_static("\n")

    session.connect(s_get("ata_pass_through"))



    session.fuzz()

def go_vm():

    if len(sys.argv) != 3 :
        print "Usage: sudo python controller.py <option> <filename>"

    input=sys.argv[2]
    machines=[]
    with open(input) as fd:
        for line in fd:
            machine=vm.Vm(sys.argv[1],line.split())
            machines.append(machine)
            machine.start()

    for m in machines:
        m.join()

    return



def go_offline():

    if len(sys.argv) != 4 :
        print "Usage: sudo python controller.py <option> <filename_input> <filename_commands>"

    input=sys.argv[2]
    cmds=sys.argv[3]
    with open(input) as fd:
        line=fd.readline()
        machine=vm.Vm(sys.argv[1],line.split(),filename=cmds)
        machine.start()
        machine.join()


    return


if __name__ == "__main__":

    if sys.argv[1]=='-vm':
        go_vm()
    elif sys.argv[1]=='-r':
        go_offline()
    else:
        print 'Available options: -vm / -r'

  #  main()

