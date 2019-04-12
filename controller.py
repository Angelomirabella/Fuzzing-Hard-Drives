import sys
import vm
from boofuzz import *

def main():

    if len(sys.argv) != 4:
        print "Usage: sudo  python controller.py <option> <port> <iterations>"
        exit(0)


    session = Session(target=Target(connection=SocketConnection("127.0.0.1", int(sys.argv[2]), proto='tcp')))

    s_initialize("ata_pass_through")
    s_byte(0xa1,fuzzable=False) #not fuzzable
    s_byte(0xc,fuzzable=False) #not fuzzable 6<<1  / 4<<1
    s_byte(0x2e,fuzzable=False)
    s_random(0x000000000040250000,9,9,int(sys.argv[3]))


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
            print machine.id, line
            machines.append(machine)
            machine.start()

    for m in machines:
        print m.id
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

def go_proc():
    if len(sys.argv) != 6:
        print "Usage: sudo python controller.py <option> <id> <dst_port> <ykush_port> <iterations>"

    args=[ sys.argv[i] for i in range(len(sys.argv)) if i > 1]
    machine=vm.Vm('-vm', args )
    machine.run()




if __name__ == "__main__":

    if sys.argv[1]=='-vm':
        go_vm()
    elif sys.argv[1]=='-r':
        go_offline()
    elif sys.argv[1]=='-p':
        main()
    elif sys.argv[1]=='-proc':
        go_proc()
    else:
        print 'Available options: -vm  -p -proc -r '



