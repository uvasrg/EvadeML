import sys, os
from pdfrate_wrapper import pdfrate
from hidost_wrapper import hidost
import math

def hidost_pdfrate(file_paths):
    # hidost = lambda *args:query_classifier('hidost', *args)
    # pdfrate = lambda *args:query_classifier('pdfrate', *args)

    hidost_scores = hidost(file_paths)
    pdfrate_scores = pdfrate(file_paths)
    pdfrate_scores_norm = [score-0.5 for score in pdfrate_scores]
    assert(len(hidost_scores) == len(pdfrate_scores) == len(file_paths))

    scores = []

    for i in range(len(file_paths)):
        p_score = pdfrate_scores_norm[i]
        h_score = hidost_scores[i]

        if p_score * h_score <= 0:
            # When the two disagree, 
            # the result is malicious as long as one of them classify as malicious.
            # Note: assume 0 is malicious.
            if p_score < 0:
                p_score = 0
            if h_score < 0:
                h_score = 0

        score = (p_score + h_score)
        scores.append(score)
    return scores

def sigmoid(x):
    return 1 / (1 + math.exp(-x))

def hidost_pdfrate_sigmoid(file_paths):
    # hidost = lambda *args:query_classifier('hidost', *args)
    # pdfrate = lambda *args:query_classifier('pdfrate', *args)

    hidost_scores = hidost(file_paths)
    pdfrate_scores = pdfrate(file_paths)
    assert(len(hidost_scores) == len(pdfrate_scores) == len(file_paths))

    hidost_scores = map(sigmoid, hidost_scores)

    hidost_scores = map(lambda x:x-0.5, hidost_scores)
    pdfrate_scores = map(lambda x:x-0.5, pdfrate_scores)

    scores = []

    for i in range(len(file_paths)):
        p_score = pdfrate_scores[i]
        h_score = hidost_scores[i]
 
        if p_score * h_score <= 0:
            # When the two disagree, 
            # the result is malicious as long as one of them classify as malicious.
            # Note: assume 0 is malicious.
            if p_score < 0:
                p_score = 0
            if h_score < 0:
                h_score = 0

        score = (p_score + h_score)
        scores.append(score)
    return scores

if __name__ == '__main__':
    pdf_list = sys.argv[1:]
    pdf_paths = map(os.path.abspath, pdf_list)

    results = hidost_pdfrate(pdf_paths)
    print results