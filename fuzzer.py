import socket
import signal
import ata
import threading
import Queue
import sys
import subprocess
import random
import string
import time
import os

RES_LEN=104 #56
ATA_PASS_THROUGH_LEN=12
serial_no_origin='14380D4A644F'
fw_rev_origin='MU01'
model_origin='Crucial_CT256MX100SSD1'

queue=Queue.Queue()
sem=threading.Semaphore(0)
stop=False
lock = threading.Lock()


def randomString(stringLength=10):
    """Generate a random string of fixed length """
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))

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
        ata_pass_through= queue.get()
        if len(ata_pass_through) != 12:
            continue
        print hex(ata_pass_through['opcode']), hex(ata_pass_through['protocol']), hex(ata_pass_through['flags']),hex(ata_pass_through['features']),hex(ata_pass_through['sector_count']),hex(ata_pass_through['lba_low']),hex(ata_pass_through['lba_mid']),hex(ata_pass_through['lba_high']),hex(ata_pass_through['device']),hex(ata_pass_through['command']),hex(ata_pass_through['reserved']),hex(ata_pass_through['control'])

        res = ata.ReadBlockSgIo("/dev/"+sys.argv[3], ata_pass_through)
        i += 1
        print res
        print 'Done ', str(i)







def go_live():
    global stop

    if len(sys.argv) != 4:
        print "Usage: sudo python server.py <option> <port> <device>"
        exit(0)
    signal.signal(signal.SIGINT, quit_handler)
    t = threading.Thread(target=work)
    t.start()

    s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.bind(('',int(sys.argv[2])))
    s.listen(5)
    print 'Waiting Connections...'
    i=1

    while True:
        client_s, addr= s.accept()
        raw_data = ''
        while len(raw_data) < ATA_PASS_THROUGH_LEN+1:
            more = client_s.recv((ATA_PASS_THROUGH_LEN+1) - len(raw_data))
            if not more:
                raise EOFError()
            raw_data += more
            #raw_data=client_s.recv(13)


        ata_pass_through={'opcode' : int(ord(raw_data[0])) , 'protocol' :  int(ord(raw_data[1])) , 'flags' :  int(ord(raw_data[2])) , 'features' :  int(ord(raw_data[3]))
        , 'sector_count' :  int(ord(raw_data[4])) , 'lba_low' :  int(ord(raw_data[5])) , 'lba_mid' :  int(ord(raw_data[6])) , 'lba_high' :  int(ord(raw_data[7]))
        ,  'device' :  int(ord(raw_data[8])) , 'command' :  int(ord(raw_data[9])) , 'reserved' :  int(ord(raw_data[10])) , 'control' :  int(ord(raw_data[11]))}

        queue.put(ata_pass_through)
        sem.release()
        i+=1

def go_qemu():

    if len(sys.argv) != 4:
        print "Usage: sudo python server.py <option> <port> <device>"
        exit(0)

    signal.signal(signal.SIGINT, quit_handler)

    s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.bind(('',int(sys.argv[2])))
    s.listen(5)
    print 'Waiting Connections...'
    i=0

    while True:
        client_s, addr= s.accept()
        raw_data = ''
        while len(raw_data) < ATA_PASS_THROUGH_LEN+1:
            more = client_s.recv((ATA_PASS_THROUGH_LEN+1) - len(raw_data))
            if not more:
                raise EOFError()
            raw_data += more
            #raw_data=client_s.recv(13)


        ata_pass_through={'opcode' : int(ord(raw_data[0])) , 'protocol' :  int(ord(raw_data[1])) , 'flags' :  int(ord(raw_data[2])) , 'features' :  int(ord(raw_data[3]))
        , 'sector_count' :  int(ord(raw_data[4])) , 'lba_low' :  int(ord(raw_data[5])) , 'lba_mid' :  int(ord(raw_data[6])) , 'lba_high' :  int(ord(raw_data[7]))
        ,  'device' :  int(ord(raw_data[8])) , 'command' :  int(ord(raw_data[9])) , 'reserved' :  int(ord(raw_data[10])) , 'control' :  int(ord(raw_data[11]))}

        print  hex(ata_pass_through['opcode']), hex(ata_pass_through['protocol']), hex(ata_pass_through['flags']),hex(ata_pass_through['features']),hex(ata_pass_through['sector_count']),hex(ata_pass_through['lba_low']),hex(ata_pass_through['lba_mid']),hex(ata_pass_through['lba_high']),hex(ata_pass_through['device']),hex(ata_pass_through['command']),hex(ata_pass_through['reserved']),hex(ata_pass_through['control'])

        res = ata.ReadBlockSgIo("/dev/"+sys.argv[3], ata_pass_through)
        i += 1


        #Test Checks - 1 file system

        try:
            name='test_file.txt'
            fd=open(name,'w')
            fd.write('ciao mamma\n')
            fd.flush()
            fd.close()
            fd=open(name,'r')
            tmp=fd.readline()
            if tmp != 'ciao mamma\n':
                print 'Read content is different from expected! -> ' , tmp
                sys.stdout.flush()
            fd.close()
            #os.remove(name)
        except:
            print 'Exception in file system check. Probably it it read only!'
            sys.stdout.flush()
            exit(-1)

        #Check 2 - Identify
        serial_no, fw_rev, model = ata.GetDriveIdSgIo_Origin(sys.argv[3])
        if serial_no != 'QM00005' or fw_rev != '2.5+' or model != 'QEMU HARDDISK':
            print 'Identify test failed -->  values: ' , serial_no, fw_rev, model

        print res
        print 'Done ', str(i)
        sys.stdout.flush()
        client_s.shutdown(socket.SHUT_RDWR)
        client_s.close()


def go_vm():

    if len(sys.argv) != 4:
        print "Usage: sudo python server.py <option> <host_port> <size>"
        exit(0)
    signal.signal(signal.SIGINT, quit_handler)

    s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.bind(('',int(sys.argv[2])))
    s.listen(5)
    i=1

    fd=open('log.txt','a')

    while True:
        client_s, addr = s.accept()
        raw_data = ''

        while len(raw_data) < ATA_PASS_THROUGH_LEN+1:
            more = client_s.recv((ATA_PASS_THROUGH_LEN+1) - len(raw_data))
            if not more:
                raise EOFError()
            raw_data += more


        ata_pass_through = {'opcode': int(ord(raw_data[0])), 'protocol': int(ord(raw_data[1])),
                            'flags': int(ord(raw_data[2])), 'features': int(ord(raw_data[3]))
            , 'sector_count': int(ord(raw_data[4])), 'lba_low': int(ord(raw_data[5])), 'lba_mid': int(ord(raw_data[6])),
                           'lba_high': int(ord(raw_data[7]))
            , 'device': int(ord(raw_data[8])), 'command': int(ord(raw_data[9])), 'reserved': int(ord(raw_data[10])),
                            'control': int(ord(raw_data[11]))}

        cmd=""
        for i in range(ATA_PASS_THROUGH_LEN):
            cmd += "0x{:02x}".format(ord(raw_data[i]))
            cmd += " "
        client_s.sendall(cmd)
        cnt=0
        while  True:
        #    proc = subprocess.Popen(["lsblk | grep " + dev + " | wc -l"], stdout=subprocess.PIPE, shell=True)
            fd.write('in loop\n')
            proc = subprocess.Popen(["lsblk | grep " + sys.argv[3] +" | awk '{print $1;}'"], stdout=subprocess.PIPE, shell=True)
            (out, err) = proc.communicate()
            fd.write('a')
            fd.write(out+ ' \n')
            fd.write('b\n')
            dev=out[:-1]
            if len(dev)>0:
                break
            else:
                time.sleep(1)
                cnt= cnt + 1
                if cnt == 30: #ssd is not recovering - shut down everything
                    client_s.sendall(b'\x00' * RES_LEN) #56 = RES_LEN
                #    client_s.shutdown(socket.SHUT_RDWR)
                 #   client_s.close()
                  #  exit(-1)
                    client_s.recv(1)
                    proc = subprocess.Popen(["lsblk | grep " + sys.argv[3] + " | wc -l"], stdout=subprocess.PIPE,shell=True)
                    (out, err) = proc.communicate()
                    fd.write('out ' + out + '\n')

                    proc = subprocess.Popen(["lsblk "], stdout=subprocess.PIPE,shell=True)
                    (out, err) = proc.communicate()
                    fd.write('lsblk ' + out + '\n')


                    client_s.sendall(out[0])
                    return


        try:
            res = ata.ReadBlockSgIo("/dev/"+ dev, ata_pass_through)
        except:
            res=b'\x01'*RES_LEN

        fd.write('res ' + res + '\n')
        client_s.sendall(res)

        proc = subprocess.Popen(["lsblk | grep " + sys.argv[3] + " | wc -l"], stdout=subprocess.PIPE,shell=True)
 #       proc = subprocess.Popen(["lsblk | grep " + dev + " | wc -l"], stdout=subprocess.PIPE, shell=True)

        (out, err) = proc.communicate()
        fd.write('out ' + out  + '\n')
        if err is not None:
            fd.write('err ' + err + '   \n')
        fd.flush()
        if int(out) == 0: #if 0 ssd is dead - Try to unplug and replug
            client_s.sendall(out[0])
            client_s.recv(1)
            for i in range(10):
                proc = subprocess.Popen(["lsblk | grep " + sys.argv[3] + " | wc -l"], stdout=subprocess.PIPE, shell=True)
#               proc = subprocess.Popen(["lsblk | grep " + dev + " | wc -l"], stdout=subprocess.PIPE, shell=True)
                (out, err) = proc.communicate()
                fd.write('recovering ' + str(i) + ' ' + out + '\n')
                if int(out)==1:
                    break
                time.sleep(1)
            client_s.sendall(out[0])
            if int(out) == 0:  # ssd still disconnected - ask controller to shut down the vm and exit the process otherwise continue
                client_s.shutdown(socket.SHUT_RDWR)
                client_s.close()
                exit(-1)

        else: #  out > 0 BUT  double-check with Identify command
            #print 'Verify Identify'
            serial_no,fw_rev,model=ata.GetDriveIdSgIo_Origin(dev)
            if serial_no!=serial_no_origin or fw_rev != fw_rev_origin or model != model_origin: #cmd was somehow bad
                client_s.sendall('4')
                client_s.recv(1)
                for i in range(10):
                    proc = subprocess.Popen(["lsblk | grep " + sys.argv[3] + " | wc -l"], stdout=subprocess.PIPE,
                                            shell=True)
                    #               proc = subprocess.Popen(["lsblk | grep " + dev + " | wc -l"], stdout=subprocess.PIPE, shell=True)
                    (out, err) = proc.communicate()
                    fd.write('recovering ' + str(i) + ' ' + out + '\n')
                    if int(out) == 1:
                        break
                    time.sleep(1)
                client_s.sendall(out[0])
                if int(out) == 0:  # ssd still disconnected - ask controller to shut down the vm and exit the process otherwise continue
                    client_s.shutdown(socket.SHUT_RDWR)
                    client_s.close()
                    exit(-1)
               # print 'bad'
            else:
                client_s.sendall(out[0])
              #  print 'good'

        i += 1


def go_offline():

    if len(sys.argv) != 4:
        print "Usage: sudo python server.py <option> <filename> <size>"
        exit(0)
    i=0
    filename=sys.argv[2]

    proc = subprocess.Popen(["lsblk | grep " + sys.argv[3] +" | head -n 1 | awk '{print $1;}'"], stdout=subprocess.PIPE, shell=True)
    (out,err)=proc.communicate()
    dev=out[:-1]

    for line in open(filename):
        values=line.split()
        ata_pass_through = {'opcode': int(values[0],0), 'protocol': int(values[1],0),
                            'flags': int(values[2],0), 'features': int(values[3],0)
            , 'sector_count': int(values[4],0), 'lba_low': int(values[5],0), 'lba_mid': int(values[6],0),
                            'lba_high': int(values[7],0)
            , 'device': int(values[8],0), 'command': int(values[9],0), 'reserved': int(values[10],0),
                            'control': int(values[11],0)}
    
        print hex(ata_pass_through['opcode']), hex(ata_pass_through['protocol']), hex(ata_pass_through['flags']),hex(ata_pass_through['features']),hex(ata_pass_through['sector_count']),hex(ata_pass_through['lba_low']),hex(ata_pass_through['lba_mid']),hex(ata_pass_through['lba_high']),hex(ata_pass_through['device']),hex(ata_pass_through['command']),hex(ata_pass_through['reserved']),hex(ata_pass_through['control'])
        res=ata.ReadBlockSgIo("/dev/"+dev, ata_pass_through)
        i+=1
        proc = subprocess.Popen(["lsblk | grep " + dev + " | head -n 1 | awk '{print $4;}'"], stdout=subprocess.PIPE, shell=True)
        (out, err) = proc.communicate()

        print res
        print 'Done ' + str(i) + ' Size ' + out
        sys.stdout.flush()
        if out[:-1] != sys.argv[3]:
            print 'ERROR'
            exit(0)

def go_qemu_offline():
    if len(sys.argv) != 4:
        print "Usage: sudo python server.py <option> <filename> <device>"
        exit(0)
    i = 0
    filename = sys.argv[2]

    dev = sys.argv[3]

    for line in open(filename):
        values = line.split()
        ata_pass_through = {'opcode': int(values[0], 0), 'protocol': int(values[1], 0),
                            'flags': int(values[2], 0), 'features': int(values[3], 0)
            , 'sector_count': int(values[4], 0), 'lba_low': int(values[5], 0), 'lba_mid': int(values[6], 0),
                            'lba_high': int(values[7], 0)
            , 'device': int(values[8], 0), 'command': int(values[9], 0), 'reserved': int(values[10], 0),
                            'control': int(values[11], 0)}

        print hex(ata_pass_through['opcode']), hex(ata_pass_through['protocol']), hex(ata_pass_through['flags']), hex(
            ata_pass_through['features']), hex(ata_pass_through['sector_count']), hex(ata_pass_through['lba_low']), hex(
            ata_pass_through['lba_mid']), hex(ata_pass_through['lba_high']), hex(ata_pass_through['device']), hex(
            ata_pass_through['command']), hex(ata_pass_through['reserved']), hex(ata_pass_through['control'])
        res = ata.ReadBlockSgIo("/dev/" + dev, ata_pass_through)
        i += 1
        #Test Checks - 1 file system

        try:
            name='test_file.txt'
            fd=open(name,'w')
            fd.write('ciao mamma\n')
            fd.flush()
            fd.close()
            fd=open(name,'r')
            tmp=fd.readline()
            if tmp != 'ciao mamma\n':
                print 'Read content is different from expected! -> ' , tmp
                sys.stdout.flush()
            fd.close()
            #os.remove(name)
        except:
            print 'Exception in file system check. Probably it it read only!'
            sys.stdout.flush()
            exit(-1)

        #Check 2 - Identify
        serial_no, fw_rev, model = ata.GetDriveIdSgIo_Origin(sys.argv[3])
        if serial_no != 'QM00005' or fw_rev != '2.5+' or model != 'QEMU HARDDISK':
            print 'Identify test failed -->  values: ' , serial_no, fw_rev, model

        print res
        print 'Done ', str(i)
        sys.stdout.flush()


if __name__=='__main__':

    option=sys.argv[1]
    if option == '-i':
        go_live()
    elif option == '-n':
        go_vm()
    elif option == '-r':
        go_offline()
    elif option == '-q':
        go_qemu()
    elif option == '-qr':
        go_qemu_offline()
    else:
        print 'Usage: sudo python fuzzer.py -i <port> <device>'
        print 'Usage: sudo python fuzzer.py -n <host_port> <size>'
        print 'Usage: sudo python fuzzer.py -r <filename> <size>'
        print 'Usage: sudo python fuzzer.py -qr <filename> <device>'
