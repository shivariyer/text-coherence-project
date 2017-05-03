# TODO fix unicode issuse

import json
#import sys
import nltk
from nltk.stem import PorterStemmer
import itertools
import os
import pickle
import argparse

class CoherenceFeatureBuilder():
    def __init__(self):
        self.open_class_words = ['NN', 'NNS', 'NNP', 'NNPS', 'VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ', 'RB', 'RBR', 'RBS', 'JJ', 'JJR', 'JJS']
        self.discourse_matrix = {}
        self.all_terms = []
        self.num_sentences = []
        
    def read_input(self, input_file):
        relations = [] 
        with open(input_file, 'r') as f:
            for line in f.readlines():
                line = line.split("|")
                
                # Only taking relations between sentences
                #NOTE Ignoring this for now because of less data
                if True:#line[23] != line[33]:
                    relation = {
                            'type': line[0],
                            'conn_head': line[5],
                            'conn_head_semantic_class': line[11],
                            'arg1': line[24],
                            'arg2': line[34],
                            's1': int(line[23]),
                            's2': int(line[33])
                            }
                    relations.append(relation)
            return {"relations": relations}

    def extract_relation(self, relation, arg):
        # TODO try other stemmers
        stemmer = PorterStemmer()
        print relation[arg]
        tokens = nltk.word_tokenize(relation[arg])
        #print tokens
        terms = [stemmer.stem(_[0]) for _ in nltk.pos_tag(tokens) if _[1] in self.open_class_words]
        for term in terms:
            arg_type = "1" if term in relation["arg1"] else "2"
            arg_relation = relation['conn_head_semantic_class']+"."+arg_type 

            rel_type = (term, relation["s1"] if arg_type == "1" else relation["s2"])
            if rel_type in self.discourse_matrix:
                self.discourse_matrix[rel_type].append(arg_relation)
            else:
                self.discourse_matrix[rel_type] = [arg_relation]
        
        # Adding relation terms to global list, removing duplicates
        self.all_terms = list(set(self.all_terms + terms))

    def build_matrix(self, relations):
        for relation in relations["relations"]:
            self.extract_relation(relation, 'arg1')
            self.extract_relation(relation, 'arg2')
            self.num_sentences.extend([relation['s1'], relation['s2']])

        self.num_sentences = list(set(self.num_sentences))
        # Filling in nil values
        for term in self.all_terms:
            for num_s in self.num_sentences:
                if self.discourse_matrix.get((term, num_s), None) is None:
                    self.discourse_matrix[(term, num_s)] = [None]

    def get_permutations(self, term, s0, s1):
        unique_permut = []
        if self.discourse_matrix.get((term, s0), None) and  self.discourse_matrix.get((term, s1), None):
            for _ in itertools.product(self.discourse_matrix[(term, s0)], self.discourse_matrix[(term, s1)]):
                unique_permut.append(_)
        return [_ for _ in unique_permut] 

    def compute_sequence_probabilities(self):
        sequence_probability = {}
        total_permutations = 0
        for term in self.all_terms:
            for num_s in sorted(self.num_sentences)[:-1]:
                local_permutations = self.get_permutations(term, num_s, num_s+1)
                for lp in local_permutations:
                    if sequence_probability.get(lp, None):
                        sequence_probability[lp] += 1.0
                    else:
                        sequence_probability[lp] = 1.0
                total_permutations += len(local_permutations)
        return {k: sequence_probability[k]/total_permutations  for k in sequence_probability.keys()}

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('inputarg',
                        help='Input file or directory/folder containing input files (.pipe)')
    parser.add_argument('--skipparse', '-p', action='store_true',
                        help='Skip creation of .json from .pipe files')
    args = parser.parse_args()
    
    #input_dir = sys.argv[1]#'data/wsj_2300.txt.pipe'
    #output_dir = sys.argv[2]
    fileslist = []
    workingdir = None
    
    if os.path.isdir(args.inputarg):
        fileslist.extend([fname for fname in os.listdir(args.inputarg) if fname.endswith('.pipe')])
        workingdir = args.inputarg
    else:
        workingdir, filename = os.path.split(args.inputarg)
        fileslist.append(filename)

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
        features[filename] = cb.compute_sequence_probabilities()

    #pickle.dump(features, open('data/%s_features.pkl'%input_dir, 'wb'))
    if len(fileslist) > 0:
        with open(os.path.join(workingdir, filename + '.features.pkl'), 'wb') as pklf:
            pickle.dump(features, pklf)
