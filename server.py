import socket
import signal
import ata
import threading
import Queue
import sys

queue=Queue.Queue()
sem=threading.Semaphore(0)
stop=False


def quit_handler(signum, frame):
    global stop
    print 'SIG INT received'
    stop = True
    sem.release()
    exit(0)

def work():
    i=1
    while True:
        sem.acquire()
        if stop:
            exit(0)
        #print 'Test: ', i
        i += 1
        ata_pass_through= queue.get()
        print ata_pass_through['opcode'], ata_pass_through['protocol'], ata_pass_through['flags'],ata_pass_through['features'],ata_pass_through['sector_count'],ata_pass_through['lba_low'],ata_pass_through['lba_mid'],ata_pass_through['lba_high'],ata_pass_through['device'],ata_pass_through['command'],ata_pass_through['reserved'],ata_pass_through['control']
        res = ata.ReadBlockSgIo(sys.argv[2], ata_pass_through)

        print res







def go():
    global stop

    if len(sys.argv) != 3:
        print "Usage: sudo python server.py <port> <device>"
        exit(0)
    signal.signal(signal.SIGINT, quit_handler)
    t = threading.Thread(target=work)
#    t.daemon = True
    t.start()

    timeout=10 #seconds
    s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.bind(('',int(sys.argv[1])))
    s.listen(5000)
#    s.settimeout(15)
    print 'Waiting Connections...'
    i=1

    while True:
        try:
            client_s, addr= s.accept()
       
#            print i
            raw_data=client_s.recv(13)
            ata_pass_through={'opcode' : int(ord(raw_data[0])) , 'protocol' :  int(ord(raw_data[1])) , 'flags' :  int(ord(raw_data[2])) , 'features' :  int(ord(raw_data[3]))
            , 'sector_count' :  int(ord(raw_data[4])) , 'lba_low' :  int(ord(raw_data[5])) , 'lba_mid' :  int(ord(raw_data[6])) , 'lba_high' :  int(ord(raw_data[7]))
            ,  'device' :  int(ord(raw_data[8])) , 'command' :  int(ord(raw_data[9])) , 'reserved' :  int(ord(raw_data[10])) , 'control' :  int(ord(raw_data[11]))}
            i+=1
        
            queue.put(ata_pass_through)
            sem.release()

 #           if i == 63:
 #           for el in raw_data:
   #             print hex(ord(el)),
    #        print
        except socket.timeout:
            print 'Timeout expired!'
            stop=True
            sem.release()
            exit(0)    
if __name__=='__main__':
    go()
