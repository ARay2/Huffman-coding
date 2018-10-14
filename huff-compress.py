"""\
------------------------------------------------------------
USE: python <PROGNAME> (options)
OPTIONS:
    -h : print this help message
    -i : use this to provide filename to be compressed (default: to be provided)
    -s LABEL : use symbol modeling scheme "LABEL" (LABEL in {char, word}, default: char)
    -o FILE : output results to file FILE (default: output to stdout)
------------------------------------------------------------\
"""

import heapq
import sys, getopt, re
from six.moves import cPickle
import time
import bz2

class CommandLine:
    def __init__(self):
        opts, args = getopt.getopt(sys.argv[1:],'hi:s:o:')
        opts = dict(opts)

        if '-h' in opts:
            self.printHelp()

        if len(args) > 0:
            print("*** ERROR: no arg files - only options! ***", file=sys.stderr)
            self.printHelp()

        if '-i' in opts:
            self.filename = opts['-i']
            if self.filename.split('.')[1] == 'txt':
                self.just_name = self.filename.split('.')[0]
            else:
                print ("System can only compress text files. Please recheck input file provided.")
                sys.exit()
        else:
            print ("Need at least one input file to proceed compressing")
            sys.exit()
            
        if '-s' in opts:
            self.weighting = opts['-s']
        else:
            self.weighting = 'char'

        if '-o' in opts:
            self.outfile = opts['-o']
        else:
            self.outfile = self.just_name + ".bin"

    def printHelp(self):
        help = __doc__.replace('<PROGNAME>',sys.argv[0],1)
        print(help, file=sys.stderr)
        sys.exit()

class struct_node(object):
    def __init__(self, freq, char=None, left=None, right=None):
        self.char = char
        self.freq = freq
        self.left = left
        self.right = right

    def __lt__(self, other):
        return self.freq < other.freq

def create_dictionary(filename, weighting):
    new_string = []
    if weighting == 'char' :
        with open(filename) as f:
            for line in f:
                for c in line:
                    new_string.append(c)
                    if not c:
                        break
                    elif c:
                        if c not in dictionary:
                            dictionary[c] = 1
                        else:
                            dictionary[c]+= 1
    elif weighting == 'word' :
        with open(filename) as f:
            for line in f:
                for word in re.compile('[a-zA-Z]+|[^a-zA-Z]').findall(line):
                    if not word:
                        break
                    elif word:
                        new_string.append(word)
                        if word not in dictionary:
                            dictionary[word] = 1
                        else:
                            dictionary[word]+= 1                        
    #print (new_string)
    return new_string,dictionary
    
def Build_Huffman_Tree(dictionary):
    nodes = []
    for char in dictionary:
        nodes.append(struct_node(dictionary[char], char))
    heapq.heapify(nodes)
    while (len(nodes) > 1):
        child1 = heapq.heappop(nodes)
        child2 = heapq.heappop(nodes)
        parent = struct_node(child1.freq + child2.freq, left=child1, right=child2)
        heapq.heappush(nodes, parent)
    if nodes == []:
        return None
    else:
        return heapq.heappop(nodes)

def get_binary_weighting(huff_tree):
    binary_dictionary = {}
    def set_binary_weight(huff_node, c=""):
        if (huff_node == None): return
        if (huff_node.left == None and huff_node.right == None):
            binary_dictionary[huff_node.char] = c
            bitmap[c] = huff_node.char
        set_binary_weight(huff_node.left, c + "0")
        set_binary_weight(huff_node.right, c + "1")
    set_binary_weight(huff_tree)
    #print(binary_dictionary)
    return binary_dictionary

def encode(file, dictionary, weighting):
    huff_tree = Build_Huffman_Tree(dictionary)
    huffman_dictionary = get_binary_weighting(huff_tree)
    # print(huffman_dictionary)
    huffman_encoded = ""
    for char in file:
        if char:
            huffman_encoded += huffman_dictionary[char]

    rBits = len(huffman_encoded) % 8  
        
    if rBits:
        for p in range(8 - rBits):
            huffman_encoded += "0"

    return huffman_encoded + "{0:08b}".format((8 - rBits)%8)

def cToBytes(huffman_encoded):
        byte = bytearray()
        for p in range(0, len(huffman_encoded), 8):
            s = huffman_encoded[p:p+8]
            byte.append(int(s, 2))
        return bytes(byte)
    
if __name__ == '__main__':
    
    start = time.time()
    config = CommandLine()
    bitmap = {}
    dictionary = {}
    doc = config.filename
    weighting = config.weighting
    start1 = time.time()
    new_string, dictionary = create_dictionary(doc, weighting)
    encodedStr = encode(new_string, dictionary, weighting)
    #print(len(bitmap))
    print("The encoding took", time.time()-start1, "seconds")
    pkl_filename = config.just_name + "-symbol-model.pkl"
    start2 = time.time()
    pOut = open(pkl_filename,"wb")
    with bz2.BZ2File(pOut, 'w') as f:
        cPickle.dump(bitmap, f, protocol= -1)
    pOut.close()
    print("The creating of the pickle file took", time.time()-start2, "seconds")
    start3 = time.time()
    g = open(config.outfile, "wb")
    g.write(cToBytes(encodedStr))
    g.close()
    print("The writing to file took", time.time()-start3, "seconds")
    print("The whole code took", time.time()-start, "seconds")
