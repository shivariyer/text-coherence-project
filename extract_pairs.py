
import os
import sys
import argparse

import numpy.random as rand

rand.seed(2)

parser = argparse.ArgumentParser()
parser.add_argument('infolder', help='Folder containing the text files')
parser.add_argument('--N', default=2, type=int, help='Number of sentence pairs from each file')
parser.add_argument('outfolder', help='Output folder')

args = parser.parse_args()

print 'Extracting {} random sentence pairs from {}.'.format(args.N, args.infolder)

fileslist = [fname for fname in os.listdir(args.infolder) if not '.perm' in fname and fname.endswith('.txt')]
fileslist.sort()

print 'Total number of files:', len(fileslist)

if not os.path.exists(args.outfolder):
    os.mkdir(args.outfolder)

for count, fname in enumerate(fileslist, 1):
    print count, fname
    
    inf = open(os.path.join(args.infolder, fname))
    lines = inf.readlines()
    lines = [l for l in lines if len(l.strip()) > 0]
    
    if len(lines)-1 < args.N:
        continue
    
    indices = rand.choice(len(lines)-1, args.N, replace=False)
    inf.close()

    for num in xrange(args.N):
        outf1 = open(os.path.join(args.outfolder, os.path.splitext(fname)[0] + '.pair-{:02d}.txt'.format(num)), 'w')
        outf2 = open(os.path.join(args.outfolder, os.path.splitext(fname)[0] + '.pair-{:02d}.perm.txt'.format(num)), 'w')

        line1 = lines[indices[num]]
        line2 = lines[indices[num]+1]
        
        outf1.writelines([line1,'\n',line2,'\n'])
        outf2.writelines([line2,'\n',line1,'\n'])

        outf1.close()
        outf2.close()
