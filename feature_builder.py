import json
import sys
import nltk
from nltk.stem import PorterStemmer

open_class_words = ['NN', 'NNS', 'NNP', 'NNPS', 'VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ', 'RB', 'RBR', 'RBS', 'JJ', 'JJR', 'JJS']
discourse_matrix = {}
all_terms = []

def read_input(input_file):
    relations = [] 
    with open(input_file, 'r') as f:
        for line in f.readlines():
            line = line.split("|")
            
            # Only taking relations between sentences
            if True:#line[23] != line[33]:
                relation = {
                        'type': line[0],
                        'conn_head': line[5],
                        'conn_head_semantic_class': line[11],
                        'arg1': line[24],
                        'arg2': line[34],
                        's1': line[23],
                        's2': line[33]
                        }
                relations.append(relation)
        return {"relations": relations}

def extract_relation(relation, arg):
    global all_terms
    # TODO try other stemmers
    stemmer = PorterStemmer()
    tokens = nltk.word_tokenize(relation[arg])
    terms = [stemmer.stem(_[0]) for _ in nltk.pos_tag(tokens) if _[1] in open_class_words]
    for term in terms:
        arg_type = "1" if term in relation["arg1"] else "2"
        arg_relation = relation['conn_head_semantic_class']+"."+arg_type 

        rel_type = (term, relation["s1"] if arg_type == "1" else relation["s2"])
        if rel_type in discourse_matrix:
            discourse_matrix[rel_type].append(arg_relation)
        else:
            discourse_matrix[rel_type] = [arg_relation]
    
    # Adding relation terms to global list, removing duplicates
    all_terms = list(set(all_terms + terms))

def build_matrix(relations):
    num_sentences = []
    for relation in relations["relations"]:
        extract_relation(relation, 'arg1')
        extract_relation(relation, 'arg2')
        num_sentences.extend([relation['s1'], relation['s2']])

    num_sentences = list(set(num_sentences))
    # Filling in nil values
    for term in all_terms:
        for num_s in num_sentences:
            if discourse_matrix.get((term, num_s), None) is None:
                discourse_matrix[(term, num_s)] = None
    

input_file = sys.argv[1]#'data/wsj_2300.txt.pipe'
parsed_file = input_file+'.json'
parse = False#True
if parse:
    relations = read_input(input_file)
    f = open(parsed_file, 'w')
    f.write(json.dumps(relations, indent=4))
else:
    f = open(parsed_file, 'r')
    relations = json.loads(f.read())
build_matrix(relations)
print discourse_matrix

