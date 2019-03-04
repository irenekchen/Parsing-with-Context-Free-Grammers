"""
COMS W4705 - Natural Language Processing - Fall 2018
Homework 2 - Parsing with Context Free Grammars 
Daniel Bauer
"""
import math
import sys
from collections import defaultdict
import itertools
from grammar import Pcfg
from six import string_types

### Use the following two functions to check the format of your data structures in part 3 ###
def check_table_format(table):
    """
    Return true if the backpointer table object is formatted correctly.
    Otherwise return False and print an error.  
    """
    if not isinstance(table, dict): 
        sys.stderr.write("Backpointer table is not a dict.\n")
        return False
    for split in table: 
        if not isinstance(split, tuple) and len(split) ==2 and \
          isinstance(split[0], int)  and isinstance(split[1], int):
            sys.stderr.write("Keys of the backpointer table must be tuples (i,j) representing spans.\n")
            return False
        if not isinstance(table[split], dict):
            sys.stderr.write("Value of backpointer table (for each span) is not a dict.\n")
            return False
        for nt in table[split]:
            if not isinstance(nt, str): 
                sys.stderr.write("Keys of the inner dictionary (for each span) must be strings representing nonterminals.\n")
                return False
            bps = table[split][nt]
            if isinstance(bps, str): # Leaf nodes may be strings
                continue 
            if not isinstance(bps, tuple):
                sys.stderr.write("Values of the inner dictionary (for each span and nonterminal) must be a pair ((i,k,A),(k,j,B)) of backpointers. Incorrect type: {}\n".format(bps))
                return False
            if len(bps) != 2:
                sys.stderr.write("Values of the inner dictionary (for each span and nonterminal) must be a pair ((i,k,A),(k,j,B)) of backpointers. Found more than two backpointers: {}\n".format(bps))
                return False
            for bp in bps: 
                if not isinstance(bp, tuple) or len(bp)!=3:
                    sys.stderr.write("Values of the inner dictionary (for each span and nonterminal) must be a pair ((i,k,A),(k,j,B)) of backpointers. Backpointer has length != 3.\n".format(bp))
                    return False
                if not (isinstance(bp[0], str) and isinstance(bp[1], int) and isinstance(bp[2], int)):
                    print(bp)
                    sys.stderr.write("Values of the inner dictionary (for each span and nonterminal) must be a pair ((i,k,A),(k,j,B)) of backpointers. Backpointer has incorrect type.\n".format(bp))
                    return False
    return True

def check_probs_format(table):
    """
    Return true if the probability table object is formatted correctly.
    Otherwise return False and print an error.  
    """
    if not isinstance(table, dict): 
        sys.stderr.write("Probability table is not a dict.\n")
        return False
    for split in table: 
        if not isinstance(split, tuple) and len(split) ==2 and isinstance(split[0], int) and isinstance(split[1], int):
            sys.stderr.write("Keys of the probability must be tuples (i,j) representing spans.\n")
            return False
        if not isinstance(table[split], dict):
            sys.stderr.write("Value of probability table (for each span) is not a dict.\n")
            return False
        for nt in table[split]:
            if not isinstance(nt, str): 
                sys.stderr.write("Keys of the inner dictionary (for each span) must be strings representing nonterminals.\n")
                return False
            prob = table[split][nt]
            if not isinstance(prob, float):
                sys.stderr.write("Values of the inner dictionary (for each span and nonterminal) must be a float.{}\n".format(prob))
                return False
            if prob > 0:
                sys.stderr.write("Log probability may not be > 0.  {}\n".format(prob))
                return False
    return True



class CkyParser(object):
    """
    A CKY parser.
    """

    def __init__(self, grammar): 
        """
        Initialize a new parser instance from a grammar. 
        """
        self.grammar = grammar

    def is_in_language(self,tokens):

        rules = list(self.grammar.rhs_to_rules)
        n = len(tokens)
        table = [[[] for i in range(n+1)] for j in range(n+1)]
        
        for i in range(n):
            for rule in rules:
                if rule == (tokens[i],):
                    table[i][i+1] = set()
                    for x in self.grammar.rhs_to_rules[rule]:
                        table[i][i+1].add(x[0])
        for length in range(2, n+1): 
            for i in range(n-length+1): 
                j = i+length 
                for k in range (i+1, j): 
                    if not table[i][j]:
                        table[i][j] = set()
                    for rule in rules:
                        if len(rule) == 2:
                            for symbol1 in table[i][k]:
                                for symbol2 in table[k][j]:
                                    if symbol1 == rule[0] and symbol2 == rule[1]:
                                        for x in self.grammar.rhs_to_rules[rule]:
                                            table[i][j].add(x[0])
        for i in range(n+1):
            bleh = list()
            for j in range(n+1):
                bleh.append(table[i][j])
            print("{}, {}".format(i, bleh))
        if table[0][n-1]:
            return True     
        return False


    def parse_with_backpointers(self, tokens):

        rules = list(self.grammar.rhs_to_rules)
        n = len(tokens)
        table = dict()
        probs = dict()
        for i in range(n+1):
            for j in range(n+1): 
                table[(i,j)] = dict()
        for i in range(n+1):
            for j in range(n+1): 
                probs[(i,j)] = dict()
        
        for i in range(n):
            for rule in rules:
                if rule == (tokens[i],):
                    table[(i,i+1)] = dict()
                    probs[(i,i+1)] = dict()
                    for x in self.grammar.rhs_to_rules[rule]:
                        table[(i,i+1)][x[0]] = x[1][0]
                        probs[(i,i+1)][x[0]] = math.log(x[2])
        for length in range(2, n+1): 
            for i in range(n-length+1): 
                j = i+length 
                for k in range (i+1, j): 
                    if (i, j) not in table.keys():
                        table[(i, j)] = dict()
                        probs[(i, j)] = dict()
                    for rule in rules:
                        if len(rule) == 2:
                            #print(rule, table[(i, k)],table[(k,j)])
                            for symbol1 in table[(i, k)].keys():
                                for symbol2 in table[(k, j)].keys():
                                    if symbol1 == rule[0] and symbol2 == rule[1]:
                                        for x in self.grammar.rhs_to_rules[rule]:
                                            if not x[2] == 0:
                                                children = ((symbol1, i, k), (symbol2, k, j))
                                                probabiity = math.log(x[2]) + probs[(i, k)][symbol1] + probs[(k, j)][symbol2]
                                                if x[0] not in probs[(i, j)]:
                                                    probs[(i, j)][x[0]] = probabiity
                                                    table[(i, j)][x[0]] = children
                                                else:
                                                    current_prob = probs[(i, j)][x[0]]
                                                    if probabiity > current_prob:
                                                        probs[(i, j)][x[0]] = probabiity
                                                        table[(i, j)][x[0]] = children
                                            else:
                                                current_prob = 0
                                                if x[0] not in table[(i, j)]:
                                                    table[(i, j)][x[0]] = ((symbol1, i, k), (symbol2, k, j))
                                                    probs[(i, j)][x[0]] = current_prob
        for i in range(n+1):
            for j in range(n+1): 
                if (i,j) in table:
                    print((i,j), table[(i,j)])      

        return table, probs

def get_tree(chart, i, j, nt): 
    """
    Return the parse-tree rooted in non-terminal nt and covering span i,j.
    """ 
    # TODO: Part 4
    children = chart[(i,j)][nt]

    if isinstance(children, string_types):
        #print(nt, children)
        return (nt, children)
    left_child = children[0]
    right_child = children[1]
    #probabiity = (self.probs[(i,j)][non_term], nonterm)
    left_tree = get_tree(chart, left_child[1], left_child[2], left_child[0])
    right_tree = get_tree(chart, right_child[1], right_child[2], right_child[0])
    
    return (nt, left_tree, right_tree)
               
   
if __name__ == "__main__":
    
    with open(sys.argv[1],'r') as grammar_file: 
        grammar = Pcfg(grammar_file) 
        parser = CkyParser(grammar)
        toks =['flights', 'from', 'miami', 'to', 'cleveland','.'] 
        #toks =['miami', 'flights','cleveland', 'from', 'to','.']
        toks =['flights', 'from', 'los', 'angeles', 'to', 'pittsburgh', '.']
        #print(parser.is_in_language(toks))
        table,probs = parser.parse_with_backpointers(toks)
        #print(table)
        #print(probs)
        #print(probs[(0,6)]["TOP"])
        assert check_table_format(table)
        assert check_probs_format(probs)
        #tree = get_tree(table, 0, 6, grammar.startsymbol)
        #tree = parser.get_tree(table, 0, len(toks), grammar.startsymbol)
        #print(tree)
        

        
