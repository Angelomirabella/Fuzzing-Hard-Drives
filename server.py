import socket
import signal
import ata
import threading
import Queue
import sys

queue=Queue.Queue()
sem=threading.Semaphore(0)
stop=False
lock = threading.Lock()

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
    #    print 'Test: ', i
        i += 1
        ata_pass_through= queue.get()
        if len(ata_pass_through) != 12:
            continue
        print hex(ata_pass_through['opcode']), hex(ata_pass_through['protocol']), hex(ata_pass_through['flags']),hex(ata_pass_through['features']),hex(ata_pass_through['sector_count']),hex(ata_pass_through['lba_low']),hex(ata_pass_through['lba_mid']),hex(ata_pass_through['lba_high']),hex(ata_pass_through['device']),hex(ata_pass_through['command']),hex(ata_pass_through['reserved']),hex(ata_pass_through['control'])
 #       ata_pass_through={'opcode' : 0xa1 , 'protocol' :  0xc9 , 'flags' : 0x6d , 'features' :0x7
  #          , 'sector_count' : 0x19 , 'lba_low' : 0x88 , 'lba_mid' : 0xb6 , 'lba_high' : 0xc3
   #         ,  'device' :  0x6c, 'command' : 0x7b , 'reserved' :  0xcf, 'control' :0xf5}

        res = ata.ReadBlockSgIo(sys.argv[3], ata_pass_through)

        print 'Done'
    #    exit(0)







def go_live():
    global stop

    if len(sys.argv) != 4:
        print "Usage: sudo python server.py <option> <port> <device>"
        exit(0)
    signal.signal(signal.SIGINT, quit_handler)
    t = threading.Thread(target=work)
#    t.daemon = True
    t.start()

    timeout=10 #seconds
    s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.bind(('',int(sys.argv[2])))
    s.listen(5000)
#    s.settimeout(15)
    print 'Waiting Connections...'
    i=1

    while True:
        try:
            client_s, addr= s.accept()
       
#            print i
            raw_data = ''
            while len(raw_data) < 13:
                more = client_s.recv(13 - len(raw_data))
                if not more:
                    raise EOFError()
                raw_data += more
            #raw_data=client_s.recv(13)
            
            ata_pass_through={'opcode' : int(ord(raw_data[0])) , 'protocol' :  int(ord(raw_data[1])) , 'flags' :  int(ord(raw_data[2])) , 'features' :  int(ord(raw_data[3]))
            , 'sector_count' :  int(ord(raw_data[4])) , 'lba_low' :  int(ord(raw_data[5])) , 'lba_mid' :  int(ord(raw_data[6])) , 'lba_high' :  int(ord(raw_data[7]))
            ,  'device' :  int(ord(raw_data[8])) , 'command' :  int(ord(raw_data[9])) , 'reserved' :  int(ord(raw_data[10])) , 'control' :  int(ord(raw_data[11]))}
            
            queue.put(ata_pass_through)
            sem.release()

 #           if i == 63:
            #print 'Test : ', i,
        #    for el in raw_data:
         #       print hex(ord(el)),
          #  print
           #sys.stdout.flush()

            i+=1
        except socket.timeout:
            print 'Timeout expired!'
            stop=True
            sem.release()
            exit(0)


def go_offline():

    if len(sys.argv) != 4:
        print "Usage: sudo python server.py <option> <filename> <device>"
        exit(0)

    filename=sys.argv[2]

    for line in open(filename):
        values=line.split()
        ata_pass_through = {'opcode': int(values[0],0), 'protocol': int(values[1],0),
                            'flags': int(values[2],0), 'features': int(values[3],0)
            , 'sector_count': int(values[4],0), 'lba_low': int(values[5],0), 'lba_mid': int(values[6],0),
                            'lba_high': int(values[7],0)
            , 'device': int(values[8],0), 'command': int(values[9],0), 'reserved': int(values[10],0),
                            'control': int(values[11],0)}
    
        print hex(ata_pass_through['opcode']), hex(ata_pass_through['protocol']), hex(ata_pass_through['flags']),hex(ata_pass_through['features']),hex(ata_pass_through['sector_count']),hex(ata_pass_through['lba_low']),hex(ata_pass_through['lba_mid']),hex(ata_pass_through['lba_high']),hex(ata_pass_through['device']),hex(ata_pass_through['command']),hex(ata_pass_through['reserved']),hex(ata_pass_through['control'])
        ata.ReadBlockSgIo(sys.argv[3], ata_pass_through)

        print 'Done'


if __name__=='__main__':

    option=sys.argv[1]
    if option == '-i':
        go_live()
    elif option == '-r':
        go_offline()
    else:
        print 'Usage: sudo python server.py -i <port> <device>'
        print 'Usage: sudo python server.py -r <filename> <device>'
