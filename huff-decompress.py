import sys, getopt
from six.moves import cPickle
import time
import bz2

class CommandLine:
    def __init__(self):
        opts, args = getopt.getopt(sys.argv[1:],'hi:o:')
        opts = dict(opts)

        if '-h' in opts:
            self.printHelp()

        if len(args) > 0:
            print("*** ERROR: no arg files - only options! ***", file=sys.stderr)
            self.printHelp()

        if '-i' in opts:
            self.filename = opts['-i']
            if self.filename.split('.')[1] == 'bin':
                self.just_name = self.filename.split('.')[0]
            else:
                print ("System can only compress text files. Please recheck input file provided.")
                sys.exit()
        else:
            print ("Need at least one input file to proceed decompressing")
            sys.exit()

        if '-o' in opts:
            self.outfile = opts['-o']
        else:
            self.outfile = self.just_name + "_decompressed.txt"

    def printHelp(self):
        help = __doc__.replace('<PROGNAME>',sys.argv[0],1)
        print(help, file=sys.stderr)
        sys.exit()

def bToCode(infile):
    with open(infile,'rb') as f:
        code = ""
        byte = f.read(1)
        while  byte !=  "":
            if (len(byte)):
                byte = ord(byte)
                bits = bin(byte)[2:].rjust(8,'0')
                code+= bits
            else:
                return code
            byte = f.read(1)
    return code

def decode(code,cMap):
        
    inf = code[-8:]
    pad = int(inf, 2)

    code = code[:-8] 
    code = code[:-1*pad]

    cCode = ""
    dText = ""

    for bit in code:
        cCode += bit
        if(cCode in cMap):
            char = cMap[cCode]
            dText += char
            cCode = ""

    return dText

if __name__ == '__main__':
    start = time.time()
    config = CommandLine()
    infile = config.filename
    start1 = time.time()
    pkl_filename = config.just_name + "-symbol-model.pkl"
    with bz2.BZ2File(pkl_filename, 'rb') as f:
        cMap = cPickle.load(f)
    #print(cMap)
    print("The reading of the pickle file took ", time.time()-start1, "seconds")
    start2 = time.time()
    code = bToCode(infile)
    decodedStr = decode(code, cMap)
    print("The decoding individually, excludint the loading of the pickle file took", time.time()-start2, "seconds")
    print("The total decoding took ", time.time()-start1, " seconds")
    start3 = time.time()
    f = open(config.outfile, "w+")
    f.write(decodedStr)
    f.close()
    print ("The total time to write to text file took ", time.time()-start3, " seconds")
    print ("The total time of execution is ", time.time()-start, " seconds")
    #print("decodedStr", decodedStr)