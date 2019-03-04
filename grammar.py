"""
COMS W4705 - Natural Language Processing - Fall 2018
Homework 2 - Parsing with Context Free Grammars 
Daniel Bauer
"""

import sys
from collections import defaultdict
from math import fsum
import math

class Pcfg(object): 
    """
    Represent a probabilistic context free grammar. 
    """

    def __init__(self, grammar_file): 
        self.rhs_to_rules = defaultdict(list)
        self.lhs_to_rules = defaultdict(list)
        self.startsymbol = None 
        self.read_rules(grammar_file)      
 
    def read_rules(self,grammar_file):
        
        for line in grammar_file: 
            line = line.strip()
            if line and not line.startswith("#"):
                if "->" in line: 
                    rule = self.parse_rule(line.strip())
                    lhs, rhs, prob = rule
                    self.rhs_to_rules[rhs].append(rule)
                    self.lhs_to_rules[lhs].append(rule)
                else: 
                    startsymbol, prob = line.rsplit(";")
                    self.startsymbol = startsymbol.strip()
                    
     
    def parse_rule(self,rule_s):
        lhs, other = rule_s.split("->")
        lhs = lhs.strip()
        rhs_s, prob_s = other.rsplit(";",1) 
        prob = float(prob_s)
        rhs = tuple(rhs_s.strip().split())
        return (lhs, rhs, prob)

    def verify_grammar(self):
        """
        Return True if the grammar is a valid PCFG in CNF.
        Otherwise return False. 
        """
        """
        RULES:
        - either two values on rhs nonterminals (are capital) OR one value on RHS (in lower)
        - if two values on rhs, cant have nonterminal with terminal
        - if one value on rhs, cant have capital
        - for all values in lhs dictionaries, all vlaues must sum up to 1
        """
        # TODO, Part 1
        proability_tolerance = 0.00001
        for symbol, rules in self.lhs_to_rules.items():
            rules_probabilities = []
            for rule in rules:
                rhs = rule[1]
                rules_probabilities.append(rule[2])
                if len(rhs) == 2:
                    if not rhs[0].upper() == rhs[0] or not rhs[1].upper() == rhs[1]:
                        print("2 valuess on rhs and not both capital: {} {} for symbol {}".format(rhs[0], rhs[1], rule[0]))
                        return False
                elif len(rhs) == 1:
                    if not rhs[0].lower() == rhs[0]:
                        print("1 value in rhs and not lower: {} for symbol {}".format(rhs[0], rule[0]))
                        return False
                else:
                    return False
            sum_probability = fsum(rule[2] for rule in rules)
            if (1 - sum_probability) > proability_tolerance:
                print("proability of {} is not 1".format(sum_probability))
                return False
        return True


if __name__ == "__main__":
    #with open(sys.argv[1],'r') as grammar_file:
        #grammar = Pcfg(grammar_file)
    with open(sys.argv[1],'r') as grammar_file: 
        grammar = Pcfg(grammar_file)
        print(grammar.startsymbol)
        print(grammar.lhs_to_rules[(grammar.startsymbol)])
        if grammar.verify_grammar():
            print("Grammer is a valid PCFG in CNF.")
        else:
            print("Grammer is not a valid PCFG in CNF. Please input a valid grammar.")
            exit(0)
        for index, (symbol, rule) in enumerate(list(grammar.lhs_to_rules.items())):
            flight = "flights"
            #if ("miami",) in grammar.rhs_to_rules.keys():
                #print("yes")
            #print(grammar.lhs_to_rules[symbol][0][1][0])
            #print(grammar.lhs_to_rules[symbol][0][1][0])
                #print("True")
        #print((("miami",) in )grammar.lhs_to_rules["NP"])
        #print(grammar.lhs_to_rules[symbol][0][1][0])
        #print(grammar.rhs_to_rules[("miami",)])
        rules = list(grammar.rhs_to_rules)
        #for index, rule in enumerate(rules):
            #print(rule)
        print(math.log2(grammar.rhs_to_rules[("flights",)][1][2]))

        
