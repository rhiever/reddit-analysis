'''
    MUW for a text file. Symbols imcluded. 
    Copyright (C) 2013 Wesley A. Bowman
    
    Example:
    python MUWtext.py inputfile.txt outputfile.txt
    
    Then take the output file to http://www.wordle.net/compose, and paste.
    
'''

import sys
from collections import defaultdict

popularWords = defaultdict(int)

def main():
    
    words=""
    output=""
    Arg=[]
    
    for arg in sys.argv:
        Arg.append(arg)
    inFilename=Arg[1]
    with open(inFilename,'r') as f:
        for line in f:
            for word in line.split():
                popularWords[word]+=1
                words+=word+" "
                    
    outFileName = Arg[2]
    
    with open(outFileName, "w") as outFile:
    
        for word in sorted(popularWords, key=popularWords.get, reverse=True):

            if popularWords[word] > 5:
    
                txt = word + ":" + str(popularWords[word]) + "\n"
                txt = txt.encode("UTF-8")
                output += txt
                outFile.write(txt)

if __name__ == '__main__':
    sys.exit(main())

