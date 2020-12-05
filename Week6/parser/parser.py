import nltk
import sys
import re

TERMINALS = """
Adj -> "country" | "dreadful" | "enigmatical" | "little" | "moist" | "red"
Adv -> "down" | "here" | "never"
Conj -> "and" | "until"
Det -> "a" | "an" | "his" | "my" | "the"
N -> "armchair" | "companion" | "day" | "door" | "hand" | "he" | "himself"
N -> "holmes" | "home" | "i" | "mess" | "paint" | "palm" | "pipe" | "she"
N -> "smile" | "thursday" | "walk" | "we" | "word"
P -> "at" | "before" | "in" | "of" | "on" | "to"
V -> "arrived" | "came" | "chuckled" | "had" | "lit" | "said" | "sat"
V -> "smiled" | "tell" | "were"
"""

NONTERMINALS = """
S -> NP VP | S Conj S | S Conj VP
NP -> N | Det NP | AP NP | PP NP
VP -> V | VP NP | Adv VP | VP Adv | VP PP
PP -> P NP | P S
AP -> Adj | Adj AP
"""

grammar = nltk.CFG.fromstring(NONTERMINALS + TERMINALS)
parser = nltk.ChartParser(grammar)


def main():

    # If filename specified, read sentence from file
    if len(sys.argv) == 2:
        with open(sys.argv[1]) as f:
            s = f.read()

    # Otherwise, get sentence as input
    else:
        s = input("Sentence: ")

    # Convert input into list of words
    s = preprocess(s)

    # Attempt to parse sentence
    try:
        trees = list(parser.parse(s))
    except ValueError as e:
        print(e)
        return
    if not trees:
        print("Could not parse sentence.")
        return

    # Print each tree with noun phrase chunks
    for tree in trees:
        tree.pretty_print()

        print("Noun Phrase Chunks")
        for np in np_chunk(tree):
            print(" ".join(np.flatten()))


def preprocess(sentence):
    """
    Convert `sentence` to a list of its words.
    Pre-process sentence by converting all characters to lowercase
    and removing any word that does not contain at least one alphabetic
    character.
    """
    
    # Seperate words
    words = nltk.word_tokenize(sentence)

    lowerCaseWords = [] # Words made lowercase

    # Make lowercase and determine words to remove 
    # that are entirely non-alphabetic
    for word in words:
        
        # Check if any alphabetic characters in word
        isAlpha = True if re.search('[a-zA-Z]', word) is not None else False

        # Only add words with some alpha character
        if isAlpha:
        
            # Make lowercase
            wordLower = word.lower()

            # Add to new list
            lowerCaseWords.append(wordLower)
        
    
    return lowerCaseWords
            

def np_chunk(tree):
    """
    Return a list of all noun phrase chunks in the sentence tree.
    A noun phrase chunk is defined as any subtree of the sentence
    whose label is "NP" that does not itself contain any other
    noun phrases as subtrees.
    """
    
    npChunks = []

    # Iterate over every subtree with a NP
    for subtree in tree.subtrees(filter= lambda t: t.label() == "NP"):
        # If it contains a NP then it is not the lowest
        if not containsNP(subtree):
            npChunks.append(subtree)
            
    return npChunks

def containsNP(tree):

    for subtree in tree:
        
        if type(subtree) == nltk.tree.Tree:
            if subtree.label() == 'NP':
                return True
            containsNP(subtree)
        else:
            return False


if __name__ == "__main__":
    main()
