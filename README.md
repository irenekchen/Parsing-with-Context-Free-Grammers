# Parsing-with-Context-Free-Grammers
Implementation of the CKY algorithm for CFG and PCFG parsing.

## Data files:

The main data for this project has been extracted from the ATIS (Air Travel Information Services) subsection of the Penn Treebank. ATIS is originally a spoken language corpus containing user queries about air travel. These queries have been transcribed into text and annotated with Penn-Treebank phrase structure syntax.
The data set contains sentences such as  "what is the price of flights from indianapolis to memphis ."

There were 576 sentences in total, out of which 518 were used for training (extracting the grammar and probabilites) and 58 for test. The data set is obviously tiny compared to the entire Penn Treebank and typically that would not be enough training data. However, because the domain is so restricted, the extracted grammar is actually able to generalize reasonably well to the test data. 

There are 2 data files:
atis3.pcfg - contains the PCFG grammar (980 rules)
atis3_test.ptb - contains the test corpus (58 sentence).

The tree structures for atis3_test.ptb are a little different from what we have seen in class. Consider the following example from the test file: 

```
(TOP (S (NP i) (VP (WOULD would) (VP (LIKE like) (VP (TO to) (VP (TRAVEL travel) (PP (TO to) (NP westchester))))))) (PUN .))
```

![Constituency tree](/constituency_tree.png)

Note that there are no part of speech tags. In some cases phrases like NP directly project to the terminal symbol (NP -> westchester). In other cases, nonterminals for a specific word were added (TRAVEL -> travel).
The start-symbol for the grammar (and therefore the root for all trees) is "TOP". This is the result of an automatic conversion to make the tree structure compatible with the grammar in Chomsky Normal Form. 

# Reading the grammar and getting started

The class Pcfg represents a PCFG grammar in chomsky normal form. To instantiate a Pcfg object, you need to pass a file object to the constructor, which contains the data. For example: 

```
with open('atis3.pcfg','r') as grammar_file: 
    grammar = Pcfg(grammar_file)
```

The instance variables of the Pcfg instance can be accessed to get information about the rules: 

```
>>> grammar.startsymbol
'TOP'
```

The dictionary lhs_to_rules maps left-hand-side (lhs) symbols to lists of rules. For example, we will want to look up all rules of the form PP -> ??

```
>>> grammar.lhs_to_rules['PP']
[('PP', ('ABOUT', 'NP'), 0.00133511348465), ('PP', ('ADVP', 'PPBAR'), 0.00133511348465), ('PP', ('AFTER', 'NP'), 0.0253671562083), ('PP', ('AROUND', 'NP'), 0.00667556742323), ('PP', ('AS', 'ADJP'), 0.00133511348465), ... ]
```

Each rule in the list is represented as (lhs, rhs, probability) triple. So the first rule in the list would be 

*PP -> ABOUT NP* with *PCFG* probability 0.00133511348465.

The *rhs_to_rules* dictionary contains the same rules as values, but indexed by right-hand-side. For example: 

```
>>> grammar.rhs_to_rules[('ABOUT','NP')]
[('PP', ('ABOUT', 'NP'), 0.00133511348465)]

>>> grammar.rhs_to_rules[('NP','VP')]
[('NP', ('NP', 'VP'), 0.00602409638554), ('S', ('NP', 'VP'), 0.694915254237), ('SBAR', ('NP', 'VP'), 0.166666666667), ('SQBAR', ('NP', 'VP'), 0.289156626506)]
```

The method verify_grammar, checks that the grammar is a valid PCFG in CNF. We check that the rules have the right format and that all probabilities for the same lhs symbol sum to 1.0. 
We then read in the grammar, print out a confirmation if the grammar is a valid PCFG in CNF or print an error message if it is not. 

# Membership checking with CKY 

The file cky.py contains a class CkyParser. When a CkyParser instance is created an instance is passed to the constructor. The instance variable grammar can then be used to access this Pcfg object. 

The method is_in_language(self, tokens) implements the CKY algorithm. The method reads in a list of tokens and return True if the grammar can parse this sentence and False otherwise. For example: 

```
>>> parser = CkyParser(grammar)
>>> toks =['flights', 'from', 'miami', 'to', 'cleveland', '.']  // Or: toks= 'flights from miami to cleveland .'.split()
>>> parser.is_in_language(toks)
True
>>> toks =['miami', 'flights','cleveland', 'from', 'to','.']
>>> parser.is_in_language(toks)
False
```

The ATIS grammar actually overgenerates a lot, so many unintuitive sentences can be parsed. So for this, we create a small test grammar and test cases. 

# Parsing with backpointers

The previous parsing method can identify if a string is in the language of the grammar, but it does not produce a parse tree. It also does not take probabilities into account. Thus, we extend the parser so that it retrieves the most probable parse for the input sentence, given the PCFG probabilities in the grammar. 

The method parse_with_backpointers(self, tokens) takes in a list of tokens as input and returns a parse table, and a probability table. Both objects should are constructed during parsing. 

The first object is a parse table containing backpointers, represented as a dictionary. The keys of the dictionary are spans, for example table[(0,3)] retrieves the entry for span 0 to 3 from the chart. The values of the dictionary are dictionaries that map nonterminal symbols to backpointers. For example: table[(0,3)]['NP'] returns the backpointers to the table entries that were used to create the NP phrase over the span 0 and 3. For example, the value of table[(0,3)]['NP'] could be (("NP",0,2),("FLIGHTS",2,3)). This means that the parser has recognized an NP covering the span 0 to 3, consisting of another NP from 0 to 2 and FLIGHTS from 2 to 3. The split recorded in the table at table[(0,3)]['NP'] is the one that results in the most probable parse for the span [0,3] that is rooted in NP. 
Terminal symbols in the table are just be represented as strings. For example the table entry for table[(2,3)]["FLIGHTS"] should be "flights".

The second object is similar, but records log probabilities instead of backpointers. For example the value of probs[(0,3)]['NP'] might be -12.1324. This value represents the log probability of the best parse tree (according to the grammar) for the span 0,3 that results in an NP.

The parse_with_backpointers(self, tokens) method can be called like this: 
```
>>> parser = CkyParser(grammar)
>>> toks =['flights', 'from', 'miami', 'to', 'cleveland', '.'] 
>>> table, probs = parser.parse_with_backpointers(toks)
```
During parsing, when an entry on the backpointer parse table is filled and we iterate through all the possible splits for a (span/nonterminal) combination, that entry on the table will contain the back-pointers for the the current-best split we have found so far. For each new possible split, we check if that split would produce a higher log probability. If so, we update the entry in the backpointer table, as well as the entry in the probability table. 

After parsing has finished, the table entry table[0,len(toks)][grammar.startsymbol] will contain the best backpointers for the left and right subtree under the root node. probs[0,len(toks)][grammar.startsymbol] will contain the total log-probability for the best parse. 

cky.py contains two test functions check_table_format(table) and check_prob_format(probs) can be used to make sure the two table data structures are formatted correctly (both functions should return True). Passing this test does not guarantee that the content of the tables is correct, just that the data structures are probably formatted correctly. 

```
>>> check_table_format(table)
True
>>> check_prob_format(probs)
True
```

# Retrieving a parse tree

Now that we have a working parser, we can evaluate its performance by reconstructing a parse tree from the backpointer table returned by parse_with_backpointers.

The function get_tree(chart, i,j, nt) returns the parse-tree rooted in non-terminal nt and covering span i,j.

For example:
```
>>> parser = CkyParser(grammar)
>>> toks =['flights', 'from', 'miami', 'to', 'cleveland', '.'] 
>>> table, probs = parser.parse_with_backpointers(toks)
>>> get_tree(table, 0, len(toks), grammar.startsymbol)
('TOP', ('NP', ('NP', 'flights'), ('NPBAR', ('PP', ('FROM', 'from'), ('NP', 'miami')), ('PP', ('TO', 'to'), ('NP', 'cleveland')))), ('PUN', '.'))
```
The intended format is the same as the data in the treebank. Each tree is represented as tuple where the first element is the parent node and the remaining elements are children. Each child is either a tree or a terminal string. 

We recursively traverse the parse chart to assemble this tree. 

# Evaluating the Parser

The program evaluate_parser.py evaluates the parser by comparing the output trees to the trees in the test data set.

The program can be run like this: 
```
python evaluate_parser.py atis3.pcfg atis3_test.ptb
```
The program imports the CKY parser class. It then reads in the test file line-by-line. For each test tree, it extracts the yield of the tree (i.e. the list of leaf nodes). It then feeds this list as input to the parser, obtains a parse chart, and then retrieves the predicted tree by calling your get_tree method. 

It then compares the predicted tree against the target tree in the following way (this is a standard approach to evaluating constiuency parsers, called PARSEVAL): 
First it obtains a set of the spans in each tree (including the nonterminal label). It then computes precision, recall, and F-score (which is the harmonic mean between precision and recall) between these two sets. The script finally reports the coverage (percentage of test sentences that had any parse), the average F-score for parsed sentences, and the average F-score for all sentences (including 0 f-scores for unparsed sentences). 

My parser implementation produces the following result on the atis3 test corpus: 

Coverage: 67%, Average F-score (parsed sentences): 0.95, Average F-score (all sentences): 0.64.
