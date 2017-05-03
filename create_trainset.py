
# take a collection of text files (each assumed to be a coherent piece
# of text / article) and run both the discourse parser and feature
# builder on each of those. Compile the features together to get the
# training set

import os
import json
import shutil
import pickle
import argparse
import subprocess
from feature_builder import CoherenceFeatureBuilder

# assume a naming convention for all training data - all files must
# end in "perm-x" where x is a number. The files ending in "perm-1"
# are the original unpermuted files (with coherence score 1). The
# others are all permuted variants, all with coherence score 0.

if __name__=='__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('dirlist', nargs='+', help='List of directories containing files')
    parser.add_argument('--level', type=int, choices=(1,2), default=1, help='Level of discourse relation tags')
    parser.add_argument('--pfilename', '-f', default='trainset.pkl', help='Name of output pickle file to store training set')

    args = parser.parse_args()

    features = {}
    
    for rootdir in args.dirlist:

        fileslist = [fname for fname in os.listdir(rootdir) if '.perm' in fname]
        fileslist.sort()

        print 'Number of files:', len(fileslist)
        
        for filename in fileslist:
            
            filepath = os.path.join(rootdir, filename)
            print '\nProcessing', filepath

            # run the discourse parser on the file first to create the .pipe file
            # TODO
            print 'Copying config.properties for level {} ...'.format(args.level)
            if args.level == 1:
                shutil.copy2('config.properties.level1', 'config.properties')
            else:
                shutil.copy2('config.properties.level2', 'config.properties')

            print 'Running discourse parser ...'
            parserprocess = subprocess.Popen(['java', '-jar', 'parser.jar', filepath],
                                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdoutdata, stderrdata = parserprocess.communicate()
            pipefilepath = os.path.join(os.path.dirname(filepath),
                                        'output_level{}'.format(args.level),
                                        filename + '.pipe')
            
            if parserprocess.returncode != 0 or not os.path.exists(pipefilepath):
                print stdoutdata, '\n', stderrdata
                raise Exception('Parser unsuccessful. Return code = ' + parserprocess.returncode)

            print 'Success.'
            print 'Building discourse role matrix ...'
            
            # next, run the feature builder on the output .pipe file
            cb = CoherenceFeatureBuilder()
            relations = cb.read_input(pipefilepath)
            
            op_file = os.path.join(pipefilepath + '.json')
            f = open(op_file, 'w')
            f.write(json.dumps(relations, indent=4))
            
            cb.build_matrix(relations)
            
            if filename.endswith('.perm-1'):
                # the original text, so assumed to be coherent
                features[filepath] = (cb.compute_sequence_probabilities(), 1)
            else:
                # else incoherent, so score 0 (only binary for now)
                features[filepath] = (cb.compute_sequence_probabilities(), 0)

            print 'Done.'

    print 'Dumping all features into {}.'.format(args.pfilename)
    with open(args.pfilename, 'wb') as f:
        pickle.dump(features, f)
