
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
    parser.add_argument('dirlist', nargs='+', help='Folders containing .txt files')
    parser.add_argument('origfilesign', help='Identification for original file (perm-1 for Barzilay-Lapata, None for others)')
    parser.add_argument('--level', type=int, choices=(1,2), default=1, help='Level of discourse relation tags')
    parser.add_argument('--pfilepath', '-f', default='trainset.pkl', help='Name of output pickle file to store training set')
    parser.add_argument('--features', default='all', type=str, help='all: argument+type, arg: argument, type: discourse types')

    args = parser.parse_args()

    if args.features == 'all':
        feature_types = ['argument', 'type']
    else:
        feature_types = [args.features]

    print 'Copying config.properties for level {} ...'.format(args.level)
    if args.level == 1:
        shutil.copy2('config.properties.level1', 'config.properties')
    else:
        shutil.copy2('config.properties.level2', 'config.properties')

    # put all outputs in one big training set
    for rootdir in args.dirlist:
        
        print 'Running discourse parser on {} ...'.format(rootdir)
        parserprocess = subprocess.Popen(['java', '-jar', 'parser.jar', rootdir],
                                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdoutdata, stderrdata = parserprocess.communicate()
        pipefilesdir = os.path.join(rootdir, 'output_level{}'.format(args.level))
        pipefiles_exist = any([fname.endswith('.pipe') for fname in os.listdir(pipefilesdir)])
        
        if parserprocess.returncode != 0 or not os.path.exists(pipefilesdir) or not pipefiles_exist:
            raise Exception('Parser unsuccessful. Return code = ' + parserprocess.returncode)
        
        print 'Success.'
    
    
    features = {}
    
    print 'Building discourse role matrices ...'
    
    for rootdir in args.dirlist:

        pipedir = os.path.join(rootdir, 'output_level{}'.format(args.level))
        fileslist = [fname for fname in os.listdir(pipedir) if fname.endswith('.pipe')]
        
        for filename in fileslist:

            pipefilepath = os.path.join(pipedir, filename)
            filepath = os.path.splitext(pipefilepath)[0]
            print '\nProcessing', filepath
            
            # run the feature builder on the output .pipe file
            cb = CoherenceFeatureBuilder()
            relations = cb.read_input(pipefilepath)
            
            op_file = os.path.join(pipefilepath + '.json')
            f = open(op_file, 'w')
            f.write(json.dumps(relations, indent=4))
            f.close()
            
            cb.build_matrix(relations)

            features[filepath] = cb.compute_sequence_probabilities(feature_types)
            
            print 'Done.'

    print 'Dumping all features into {}.'.format(args.pfilepath)
    with open(args.pfilepath, 'wb') as f:
        pickle.dump(features, f)


    print 'Running the classifiers ...'

    classifierprocess = subprocess.call(['python', 'plot_classifier_comparison.py', args.pfilepath, args.origfilesign])
