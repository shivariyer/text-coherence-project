
import re
import sys
import json
import nltk
from nltk.stem import PorterStemmer
import itertools
import os
import pickle
import argparse
import unicodedata

class CoherenceFeatureBuilder():
    def __init__(self):
        self.open_class_words = ['NN', 'NNS', 'NNP', 'NNPS', 'VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ', 'RB', 'RBR', 'RBS', 'JJ', 'JJR', 'JJS']
        self.discourse_matrix = {}
        self.relation_matrix = {}
        self.all_terms = []
        self.num_sentences = []
        
    def read_input(self, input_file):
        relations = []
        with open(input_file, 'r') as f:
            alllines = f.readlines()
            
            for lineno, line in enumerate(alllines,1):
                line = line.split("|")
                
                if not len(line) == 48:
                    # this means there are '|' symbols in a text. We
                    # ignore such sentences because technically they
                    # are not complete sentences.
                    continue
                
                try:
                    # encapsulating in a try block to prevent errors
                    # due to either wrongly formatted .pipe file
                    # (unlikely) or bad symbols in input sentence

                    # Only taking relations between sentences NOTE
                    # Ignoring this for now because of less data
                    if True:#line[23] != line[33]:

                        # remove stupid unicode characters
                        #arg1str = ''.join([i for i in line[24] if ord(i) < 128 else ' '])
                        #arg2str = ''.join([i for i in line[34] if ord(i) < 128 else ' '])
                        arg1str = re.sub('[^\x00-\x7F]+', ' ', line[24])
                        arg2str = re.sub('[^\x00-\x7F]+', ' ', line[34])
                        
                        relation = {
                            'type': line[0],
                            'conn_head': line[5],
                            'conn_head_semantic_class': line[11],
                            'arg1': arg1str,
                            'arg2': arg2str,
                            's1': int(line[23]),
                            's2': int(line[33])
                        }
                        relations.append(relation)
                        
                except ValueError:
                    print >>sys.stderr, 'Problem with relation in pipe. File: {}, Line no: {}'.format(input_file, lineno)
                    continue
                
                print 'Number of relations:', len(relations)
                
            return {"relations": relations}
    
    def extract_relation(self, relation, arg, feature_type):
        # TODO try other stemmers - e.g. SnowballStemmer
        # (http://www.nltk.org/howto/stem.html) and WordNet Lemmatizer
        # (nltk.stem.wordnet.WordNetLemmatizer)
        stemmer = PorterStemmer()
        tokens = nltk.word_tokenize(relation[arg])
        terms = [stemmer.stem(postags[0]) for postags in nltk.pos_tag(tokens) if postags[1] in self.open_class_words]
        
        if feature_type == "argument":
            matrix = self.discourse_matrix
        elif feature_type == "type":
            matrix = self.relation_matrix
        
        for term in terms:
            arg_type = '1' if term in relation['arg1'] else '2'
            if feature_type == "argument":
                arg_relation = relation['conn_head_semantic_class']+"."+arg_type 
            elif feature_type == "type":
                arg_relation = relation['type']

            rel_type = (term, relation["s1"] if arg_type == "1" else relation["s2"])
            if rel_type in matrix:
                if arg_relation not in matrix[rel_type]:
                    matrix[rel_type].append(arg_relation)
            else:
                matrix[rel_type] = [arg_relation]

        
        # Adding relation terms to global list, removing duplicates
        self.all_terms = list(set(self.all_terms + terms))


    def build_matrix(self, relations):
        # Extracting argument and relation features corresponding Type & Arg in paper
        for relation in relations['relations']:
            for arg in ['arg1', 'arg2']:
                for feat_type in ['argument', 'type']:
                    self.extract_relation(relation, arg, feat_type)
            
            self.num_sentences.extend([relation['s1'], relation['s2']])

        self.num_sentences = list(set(self.num_sentences))
        
        # Filling in nil values
        for term in self.all_terms:
            for num_s in self.num_sentences:
                if self.discourse_matrix.get((term, num_s)) is None:
                    self.discourse_matrix[(term, num_s)] = [None]
                if self.relation_matrix.get((term, num_s)) is None:
                    self.relation_matrix[(term, num_s)] = [None]

    def get_permutations(self, term, s0, s1, feat_type):
        unique_permut = []
        if feat_type == 'argument':
            feature_matrix = self.discourse_matrix
        elif feat_type == 'type':
            feature_matrix = self.relation_matrix

        if feature_matrix.get((term, s0)) and feature_matrix.get((term, s1)):
            unique_permut = list(itertools.product(feature_matrix[(term, s0)], feature_matrix[(term, s1)]))
        return unique_permut

    def compute_sequence_probabilities(self, feature_types=['argument']):
        final_features = {}
        num_sentences_sorted = sorted(self.num_sentences)
        for feature_type in feature_types:
            total_permutations = 0
            sequence_probability = {}
            for term in self.all_terms:
                for num_s in num_sentences_sorted[:-1]:
                    local_permutations = self.get_permutations(term, num_s, num_s+1, feature_type)
                    #print local_permutations
                    for lp in local_permutations:
                        if sequence_probability.get(lp):
                            sequence_probability[lp] += 1.0
                        else:
                            sequence_probability[lp] = 1.0
                    total_permutations += len(local_permutations)
            final_features.update({k: sequence_probability[k]/total_permutations  for k in sequence_probability.keys()})
        #print final_features
        return final_features

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('inputarg',
                        help='Input file or directory/folder containing input files (.pipe)')
    parser.add_argument('--skipparse', '-p', action='store_true',
                        help='Skip creation of .json from .pipe files')
    parser.add_argument('--outfile', default='features',
                        help='Output file name')
    args = parser.parse_args()
    
    #input_dir = sys.argv[1]#'data/wsj_2300.txt.pipe'
    #output_dir = sys.argv[2]
    fileslist = []
    workingdir = None
    
    if os.path.isdir(args.inputarg):
        fileslist.extend([fname for fname in os.listdir(args.inputarg) if fname.endswith('.pipe')])
        workingdir = os.path.join(args.inputarg)
    else:
        workingdir, filename = os.path.split(args.inputarg)
        fileslist.append(filename)
    
    fileslist.sort()
    
    print workingdir
    print fileslist
    #parse = False#True
    features = {}
    #for filename in os.listdir(os.path.join('data', input_dir)):
    for filename in fileslist:
        
        print "Processing file:`%s" % filename
        cb = CoherenceFeatureBuilder() 
        #op_file = os.path.join('data', output_dir, filename+'.json')
        op_file = os.path.join(workingdir, filename + '.json')
        
        if not args.skipparse:
            #relations = cb.read_input(os.path.join('data', input_dir, filename))
            relations = cb.read_input(os.path.join(workingdir, filename))
            f = open(op_file, 'w')
            f.write(json.dumps(relations, indent=4))
        else:
            f = open(op_file, 'r')
            relations = json.loads(f.read())
        cb.build_matrix(relations)
        '''
        for k in cb.discourse_matrix.keys():
            print k,"==>" , cb.discourse_matrix[k]
        for k in cb.relation_matrix.keys():
            print k,"==>" ,cb.relation_matrix[k]
        '''
        features[filename] = cb.compute_sequence_probabilities(['argument', 'type'])

        # print cb.discourse_matrix
        # print cb.relation_matrix
        # print cb.all_terms
        # print cb.num_sentences
    
    #pickle.dump(features, open('data/%s_features.pkl'%input_dir, 'wb'))
    if len(fileslist) > 0:
        # if len(fileslist) >= 2:
        #     pklfpath = os.path.join(args.outputdir, '{}-{}.features.pkl'.format(fileslist[0].rsplit('.',1)[0], fileslist[-1].rsplit('.',1)[0]))
        # else:
        #     pklfpath = os.path.join(args.outputdir, '{}.features.pkl'.format(fileslist[0].rsplit('.',1)[0]))
        pklfpath = args.outfile

        print 'Writing features to', pklfpath
        with open(pklfpath, 'wb') as pklf:
            pickle.dump(features, pklf)
