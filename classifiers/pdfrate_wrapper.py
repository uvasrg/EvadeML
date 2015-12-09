import sys, os

_current_dir = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.normpath(os.path.join(_current_dir, ".."))
sys.path.append(PROJECT_ROOT)

from lib.config import config
mimicus_dir = config.get('pdfrate', 'mimicus_dir')
import_path = os.path.join(mimicus_dir, 'reproduction')
sys.path.append(import_path)

from common import *
from common import _scenarios

from mimicus.tools.featureedit import _pdfrate_feature_names as feats

import numpy as np

def _pdfrate_wrapper(ntuple):
    '''
    A helper function to parallelize calls to gdkde().
    '''
    try:
        return pdfrate_once(*ntuple)
    except Exception as e:
        return e

def pdfrate_once(classifier, scaler, file_path):
    pdf_feats = FeatureEdit(file_path)
    pdf_feats = pdf_feats.retrieve_feature_vector_numpy()
    if scaler:
        scaler.transform(pdf_feats)
    pdf_score = classifier.decision_function(pdf_feats)[0, 0]
    return pdf_score

def _pdfrate_feat_wrapper(ntuple):
    '''
    A helper function to parallelize calls to gdkde().
    '''
    try:
        return pdfrate_feature_once(*ntuple)
    except Exception as e:
        return e

def pdfrate_feature_once(classifier, scaler, file_path):
    pdf_feats = FeatureEdit(file_path)
    pdf_feats = pdf_feats.retrieve_feature_vector_numpy()
    if scaler:
        scaler.transform(pdf_feats)
    return pdf_feats

def get_classifier():
    scenario_name = "FTC"
    scenario = _scenarios[scenario_name]

    # Set up classifier
    classifier = 0
    if scenario['classifier'] == 'rf':
        classifier = RandomForest()
        print 'Using RANDOM FOREST'
    elif scenario['classifier'] == 'svm':
        classifier = sklearn_SVC()
        print 'Using SVM'
    print 'Loading model from "{}"'.format(scenario['model'])
    classifier.load_model(scenario['model'])    
    return classifier

def get_classifier_scaler(scenario_name = "FTC"):
    scenario = _scenarios[scenario_name]

    # Set up classifier
    classifier = 0
    if scenario['classifier'] == 'rf':
        classifier = RandomForest()
        print 'Using RANDOM FOREST'
    elif scenario['classifier'] == 'svm':
        classifier = sklearn_SVC()
        print 'Using SVM'
    print 'Loading model from "{}"'.format(scenario['model'])
    classifier.load_model(scenario['model'])

    # Standardize data points if necessary
    scaler = None
    if 'scaled' in scenario['model']:
        scaler = pickle.load(open(config.get('datasets', 'contagio_scaler')))
        print 'Using scaler'
    return classifier, scaler

pdfrate_classifier, pdfrate_scaler = get_classifier_scaler()
pool = multiprocessing.Pool()

def pdfrate_feature(pdf_file_paths, speed_up = True):
    classifier = pdfrate_classifier
    scaler = pdfrate_scaler

    if not isinstance(pdf_file_paths, list):
        pdf_file_paths = [pdf_file_paths]

    if speed_up == True:
        # The Pool has to be moved outside the function. Otherwise, every call of this function will result a new Pool. The processes in old Pool would not terminate.
        args = [(classifier, scaler, file_path) for file_path in pdf_file_paths]
        feats = pool.map(_pdfrate_feat_wrapper, args)
    else:
        feats = []
        for pdf_file_path in pdf_file_paths:
            pdf_feats = pdfrate_feature_once(classifier, scaler, pdf_file_path)
            feats.append(pdf_feats)

    all_feat_np = None
    for feat_np in feats:
        if all_feat_np == None:
            all_feat_np = feat_np
        else:
            all_feat_np = np.append(all_feat_np, feat_np, axis=0)
    return all_feat_np

# speed_up is for feature extraction in parallel.
def pdfrate_with_feature(all_feat_np, speed_up = True):
    classifier = pdfrate_classifier
    scores = classifier.decision_function(all_feat_np)
    scores = [s[0] for s in scores]
    return scores

# speed_up is for feature extraction in parallel.
def pdfrate(pdf_file_paths, speed_up = True):
    if type(pdf_file_paths) != list:
        pdf_file_paths = [pdf_file_paths]
    classifier = pdfrate_classifier
    all_feat_np = pdfrate_feature(pdf_file_paths, speed_up)
    scores = classifier.decision_function(all_feat_np)
    scores = [float(s[0]) for s in scores]
    return scores

def compare_feats(x1, x2):
    decreased = []
    increased = []
    same = []

    for i in range(len(x1)):
        if x2[i] > x1[i]:
            increased.append(i)
        elif x2[i] < x1[i]:
            decreased.append(i)
        else:
            same.append(i)

    return decreased, increased, same

if __name__ == "__main__":
    if sys.argv[1] == 'feature':
        print pdfrate_feature(sys.argv[2])
    elif sys.argv[1] == 'compare':
        file1, file2 = sys.argv[2], sys.argv[3]
        X = pdfrate_feature([file1, file2])
        score1, score2 = pdfrate_with_feature(X)
        print "Scores: ", score1, score2
        deleted, added, fixed = compare_feats(X[0], X[1])
        if len(deleted) > 0:
            print "decreased: ", map(lambda x: feats[x], deleted)
        if len(added) > 0:
            print "increased: ", map(lambda x: feats[x], added)


    else:
        import sys
        import time
        start = time.time()
        inputs = sys.argv[1:50]
        results = pdfrate(inputs)
        print results
        print "%.1f seconds." % (time.time() - start)
