
# preprocess Barzilay-Lapata data

# remove the name of file printed on each line so that the file just
# has one sentence per line

import os

rootdir = os.path.join('data', 'barzilay-lapata')
fileslist = [os.path.join(rootdir, 'data1', 'train-perm', fname) for fname in os.listdir(os.path.join(rootdir, 'data1', 'train-perm')) if '.perm' in fname] + [os.path.join(rootdir, 'data2', 'train-perm', fname) for fname in os.listdir(os.path.join(rootdir, 'data2', 'train-perm')) if '.perm' in fname]

newdir = 'temp'

fileslist.sort()

for fpath in fileslist:
    print fpath

    fname = os.path.basename(fpath)
    
    inf = open(fpath)
    lines = inf.readlines()
    inf.close()

    newlines = []
    for line in lines:
        ind = line.index(' ')
        #assert line[:ind-1] in fname
        newlines.append(line[ind+1:])
    #lines = [line[line.index(' ')+1:] for line in lines if line[:line.index(' ')-1] in fname]

    #outf = open('temp.txt', 'w')
    outf = open(os.path.join(newdir, fpath), 'w')
    outf.writelines(newlines)
    outf.close()
    #break
    
