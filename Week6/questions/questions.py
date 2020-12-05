import glob
import math
import os
from string import punctuation
import sys
from collections import Counter

import nltk

FILE_MATCHES = 1
SENTENCE_MATCHES = 1


def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python questions.py corpus")

    # Calculate IDF values across files
    files = load_files(sys.argv[1])
    file_words = {
        filename: tokenize(files[filename])
        for filename in files
    }
    file_idfs = compute_idfs(file_words)

    # Prompt user for query
    query = set(tokenize(input("Query: ")))

    # Determine top file matches according to TF-IDF
    filenames = top_files(query, file_words, file_idfs, n=FILE_MATCHES)

    # Extract sentences from top files
    sentences = dict()
    for filename in filenames:
        for passage in files[filename].split("\n"):
            for sentence in nltk.sent_tokenize(passage):
                tokens = tokenize(sentence)
                if tokens:
                    sentences[sentence] = tokens

    # Compute IDF values across sentences
    idfs = compute_idfs(sentences)

    # Determine top sentence matches
    matches = top_sentences(query, sentences, idfs, n=SENTENCE_MATCHES)
    for match in matches:
        print(match)


def load_files(directory):
    """
    Given a directory name, return a dictionary mapping the filename of each
    `.txt` file inside that directory to the file's contents as a string.
    """
    files = {} # Text file name : string representation of content
    
    # Read in every .txt file from directory
    for fileName in glob.glob(os.path.join(directory,"*.txt")):
        with open(fileName, 'r', encoding='UTF-8') as f:
            fileContent = f.read().replace('\n', '')
            files[os.path.split(fileName)[1]] = fileContent
    
    return files

 


def tokenize(document):
    """
    Given a document (represented as a string), return a list of all of the
    words in that document, in order.

    Process document by coverting all words to lowercase, and removing any
    punctuation or English stopwords.
    """

    # Remove punctuation
    table = str.maketrans('', '', punctuation)
    document = document.translate(table)

    # Tokenize and convert to lowercase
    wordTokens = nltk.word_tokenize(document.lower())

    # Remove stop words
    stopWords = set(nltk.corpus.stopwords.words('english'))
    wordTokens = [word for word in wordTokens if word not in stopWords]

    return wordTokens


def compute_idfs(documents):
    """
    Given a dictionary of `documents` that maps names of documents to a list
    of words, return a dictionary that maps words to their IDF values.

    Any word that appears in at least one of the documents should be in the
    resulting dictionary.
    """

    # Get one instance of every word that appears in the documents
    everyWord = {word for doc in documents.keys() for word in documents[doc]}

    idfs = {} # Store the idf's mapped to a single word
    totalDocs = len(documents)

    # Calculate every words idf
    for word in everyWord:

        # Count number of docs word appears in
        docAppearances = 0
        for doc in documents.keys():
            if word in documents[doc]:
                docAppearances += 1
        
        idfs[word] = math.log(totalDocs / docAppearances)

    return idfs


def top_files(query, files, idfs, n):
    """
    Given a `query` (a set of words), `files` (a dictionary mapping names of
    files to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the filenames of the the `n` top
    files that match the query, ranked according to tf-idf.
    """
    tfidfs = {key : 0 for key in files.keys()}

    for word in query:
        for doc in files.keys():

            # Verify that the word exits in the documents, else
            # key error would occur because idfs would not be calculated
            if word in idfs:
                tfidfs[doc] += (compute_tf(word, files[doc]) * idfs[word])
    
    # Sort the docs from best match to worst
    sortedTopDocs = sorted(tfidfs, key=tfidfs.get, reverse=True)
    
    # Return the top n docs
    return sortedTopDocs[:n]


def compute_tf(wordToCount, wordList):
    """
    Count the number of times a word appears in a file
    
    PARAMATERS
    ----------
        'wordToCount': String representing a word to count the term
            frequency
        'wordList': List of words
    
    RETURN
    ------
        Number of times the given word appeared in the given word list
    """
    tf = 0
    for word in wordList:
        if word == wordToCount:
            tf += 1
    return tf

    


def top_sentences(query, sentences, idfs, n):
    """
    Given a `query` (a set of words), `sentences` (a dictionary mapping
    sentences to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the `n` top sentences that match
    the query, ranked according to idf. If there are ties, preference should
    be given to sentences that have a higher query term density.
    """

    # Score for sentences based query word idfs and term density
    scores = {key : {"idfScore" : 0, "termDensity": 0} for key in sentences.keys()}
    
    for sentence in sentences.keys():
        wordCounts = Counter(sentences[sentence])
        for word in query:
            if word in sentences[sentence]:
                scores[sentence]["idfScore"] += idfs[word]
                scores[sentence]["termDensity"] += wordCounts[word]
    
    # Sort the sentences from best match to worst
    sortedTopSent = sorted(scores, key=lambda x: 
        (scores[x]["idfScore"], scores[x]["termDensity"]), reverse=True)

    # Return the top n sentences
    return sortedTopSent[:n]
    





if __name__ == "__main__":
    main()
