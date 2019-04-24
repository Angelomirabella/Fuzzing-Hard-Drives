import subprocess
import sys





def main():

    if len(sys.argv) != 2:
        print 'Usage: sudo python starter.py <filename>'

    with open(sys.argv[1]) as fd:
        for line in fd:
            proc=subprocess.Popen(['python controller.py -proc ' + line], stdout=None, shell=True)

            #print line















if __name__=='__main__':
    main()