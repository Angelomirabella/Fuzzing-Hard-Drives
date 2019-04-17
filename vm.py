from boofuzz import *
import threading 
import os
import time
import socket
import subprocess

RES_LEN=56
CMD_LEN=60

class Vm(threading.Thread):

    def off_callback(self,sock):

        #print 'HELLOOOO'
        cmd= ''
        while len(cmd) < CMD_LEN:
            more = sock.recv(CMD_LEN - len(cmd))
            #print more, len(more)
            if not more:
                raise EOFError()
            cmd += more

       # print 'post cmd'
        res= ''
        while len(res) < RES_LEN:
            #print 'pre result'
            more = sock.recv(RES_LEN - len(res))
           # print more, len(more)
            #time.sleep(3)
            if not more:
               raise EOFError()
            res += more

        if all([el==b'\x00' for el in res]): #ssd dead for ever
            #print 'SSD DEAD ' , res
            self.out_ok.write("SSD DEAD \n")
            self.out_bad.write("SSD DEAD \n")
            sock.shutdown(socket.SHUT_RDWR)
            sock.close()
            return 0


        #print 'post res, recv alive'
        alive=sock.recv(1)
        #print 'alive 1: ' , alive
        if int(alive) > 0 :
            self.out_ok.write("Command: " + cmd+"\n")
            self.out_ok.write(res+"\n")
        else: #ssd dead - Try to unplug and replug
         #   print 'DEAD'
            self.out_bad.write("Command: " + cmd+"\n")
            self.out_bad.write(res+"\n")
            self.restart(sock)

        sock.shutdown(socket.SHUT_RDWR)
        sock.close()
        return 1

    def callback(self,target,fuzz_data_logger,session,*args,**kwargs):

        try:
            cmd = ''
            while len(cmd) < CMD_LEN:
                more = target.recv(CMD_LEN - len(cmd))
                print more, len(more)
                if not more:
                  #  exit(-1)
                    raise EOFError()
                cmd += more

            # print 'post cmd'
            res = ''
            while len(res) < RES_LEN:
                # print 'pre result'
                more = target.recv(RES_LEN - len(res))
                print more, len(more)
                # time.sleep(3)
                if not more:
                   # exit(-1)
                    raise EOFError()
                res += more

            if all([el == b'\x00' for el in res]):  # ssd dead for ever
                # print 'SSD DEAD ' , res
                self.out_ok.write("SSD DEAD \n")
                self.out_bad.write("SSD DEAD \n")

                return 0

            # print 'post res, recv alive'
            alive = target.recv(1)
            # print 'alive 1: ' , alive
            if int(alive) > 0 :
                self.out_ok.write("Command: " + cmd + "\n")
                self.out_ok.write(res + "\n")
            else:  # ssd dead - Try to unplug and replug
                print 'DEAD'
                self.out_bad.write("Command: " + cmd + "\n")
                self.out_bad.write(res + "\n")
                self.restart(target)

        except EOFError:

            if len(cmd) > 0 :
                self.out_bad.write("Command: " + cmd + " Connection resetted\n")
                if len(res)> 0 :
                    self.out_bad.write(res + "\n")
                else:
                    self.out_bad.write("No res\n")
            else:
                self.out_bad.write("Command unknown Connection resetted\n")
            self.restart(target,1)

        return 1

    def restart(self,target,skip=0):

        alive=1
        if skip==0:
            subprocess.call(["ykushcmd -d " + self.ykush_port], shell=True)

            time.sleep(0.5)
            subprocess.call(["ykushcmd -u " + self.ykush_port], shell=True)
            time.sleep(2)

            target.send(b'1')

            alive = target.recv(1)

        #    print 'alive 2: ', alive
        if int(alive) == 0 or skip==1:  # ssd dead - shut down the vm and power on again

            subprocess.call(["ykushcmd -d " + self.ykush_port], shell=True)
            subprocess.call(['vagrant halt ' + self.id + ' --force'], shell=True)

            time.sleep(0.5)
            subprocess.call(['vagrant up ' + self.id + ' --provision'], stdout=None, shell=True)

            subprocess.call(["ykushcmd -u " + self.ykush_port], shell=True)
            time.sleep(2)



    def __init__(self,option,line,filename=None):
        threading.Thread.__init__(self)
      #  print line
        self.id= line[0]
        self.dst_port=line[1]
        self.ykush_port= line[2]
        self.option=option

        if option=='-vm':
            self.live_init(line)
        elif option=='-r':
            self.offline_init(filename)



    def live_init(self,line):
        self.iterations=line[3]
        self.target=Target(connection=SocketConnection("127.0.0.1", int(self.dst_port), proto='tcp', recv_timeout=600,send_timeout=600))
        self.session=Session(target=self.target)
        self.session.register_post_test_case_callback(self.callback)
        self.out_ok=open("./output/"+str(self.id)+"_good_commands.txt","w")
        self.out_bad=open("./output/"+ str(self.id)+"_bad_commands.txt","w")

        s_initialize("ata_pass_through - " + self.id )
        s_byte(0xa1,fuzzable=False) #not fuzzable
        s_byte(0xc,fuzzable=False) #not fuzzable 6<<1  / 4<<17
        s_byte(0x2e, fuzzable=False)
        s_random(0x000000000040250000,9,9,int(self.iterations))
        s_static("\n")


        return

    def offline_init(self,filename):

        self.out_ok=open("./output/"+str(self.id)+"_good_commands_off.txt","w")
        self.out_bad=open("./output/"+ str(self.id)+"_bad_commands_off.txt","w")
        self.commands=filename

        return

    def run(self):

        if self.option=='-vm':
            self.session.connect(s_get("ata_pass_through - " + self.id))
            self.session.fuzz()
        elif self.option=='-r':

            with open(self.commands) as fd:
                for line in fd:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.connect(('localhost', int(self.dst_port)))
                    line=line[:len(line)-1]
                    line+= "a1"
                    print line
                    cmd=line.decode('hex')
            #        print len(cmd)
                    s.sendall(cmd)
                    res=self.off_callback(s)
                    if res == 0:
                        break


        self.out_ok.close()
        self.out_bad.close()

