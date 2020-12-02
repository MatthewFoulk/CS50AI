import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """

    # Probability of any page being chosen next
    pageCount = len(corpus)
    anyPageProb = (1-damping_factor) / pageCount

    # Probability of a specific linked page being chosen next
    pageLinkCount = len(corpus[page])
    if pageLinkCount > 0:   
        # Make sure links exist, so don't divide by 0
        linkedPageProb = 1 / pageLinkCount

    probDist = dict()
    
    for currPage in corpus:
        probDist[currPage] = anyPageProb
        if currPage in corpus[page]:
            # Currpage is linked to from the page parameter
            probDist[currPage] += linkedPageProb
    
    return probDist



def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """

    # Choose a random first page
    page = random.choice(list(corpus.keys()))
    generatedSamples = 1

    # Initialize page ranks starting at 0
    pageRanks = dict()
    for currPage in corpus:
        pageRanks[currPage] = 0
    
    while (generatedSamples < n):
        transitionModel = transition_model(corpus, page, DAMPING)
        
        # Choose a new page randomly based on the transition model
        page = random.choices(list(transitionModel.keys()), weights=list(transitionModel.values()), k=1)[0]
        pageRanks[page] += (1 / n)
        generatedSamples += 1
    
    return pageRanks
        



def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    pageCount = len(corpus)
    pageRanks = dict() # Store each page's rank

    # Setting the initial value for each page as equal probability
    for page in corpus:
        pageRanks[page] = 1 / pageCount

    # Update page ranks until none change more than 0.001
    change = 1
    while (change > 0.001):
        change = 0.001 # Reset change each iteration to below the min threshold
        for currPage in corpus:
            anyPageProb = (1 - damping_factor) / pageCount # Page chosen from corpus
            linkedPageProb = 0 # Page chosen from another page's links
            for otherPage in corpus:
                if currPage in corpus[otherPage]:
                    # The otherPage links to the currentPage
                    numLinks = len(corpus[otherPage])
                    otherPageRank = pageRanks[otherPage]
                    linkedPageProb += (otherPageRank / numLinks)
            linkedPageProb *= damping_factor
            newPageRank = anyPageProb + linkedPageProb
            oldPageRank = pageRanks[currPage]

            # Determine the amount of change from previous rank
            tempChange = abs(oldPageRank - newPageRank)
            if tempChange > change:
                # Update change if it was significant enough
                change = tempChange

            # Update the page's rank
            pageRanks[currPage] = newPageRank
    
    return pageRanks


if __name__ == "__main__":
    main()
