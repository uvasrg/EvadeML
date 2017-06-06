import os
from argparse import ArgumentParser
import pickle
import sys
import hashlib

_current_dir = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.normpath(os.path.join(_current_dir, ".."))
sys.path.append(PROJECT_ROOT)

from lib.config import config
exec_dir = config.get('hidost', 'exec_dir')
model_path = config.get('hidost', 'model_path')
feats_path = config.get('hidost', 'feats_path')
# temp files
cache_dir = config.get('hidost', 'cache_dir')

if config.has_option('hidost', 'sk_learn_location'):
    sk_learn_location = config.get('hidost', 'sk_learn_location')
    sys.path.insert(1, sk_learn_location)
from sklearn import datasets

pdf2paths_cmd = os.path.join(exec_dir, "pdf2paths")
feat_extract_cmd = os.path.join(exec_dir, "feat-extract")
empty_file_list = os.path.join(cache_dir, "empty.list")

def hash_str(string):
    return hashlib.sha1(string).hexdigest()

def hash_file(filepath):
    sha1 = hashlib.sha1()
    f = open(filepath, 'rb')
    try:
        sha1.update(f.read())
    finally:
        f.close()
    return sha1.hexdigest()
    
def load_features():
    feature_index_file = feats_path
    features = open(feature_index_file).readlines()
    features.pop(0)
    features = map(lambda x:x.replace('\x00\x00\n', ''), features)
    features = map(lambda x:x.replace('\x00', '/'), features)
    return features

feats = load_features()

def correct_feats_order(feats_fname, flist_fname, feats_fname_ordered):
    with open(flist_fname) as f:
        flist = [ line.strip() for line in f.readlines() ]

    with open(feats_fname) as f:
        feat_fname_list = [ line.strip().split('#') for line in f.readlines() ]

    feat_list, fname_list = zip(*feat_fname_list)
    fname_feats = dict(zip(fname_list, feat_list))
    # print flist
    feat_list_sorted = [ fname_feats[fname] for fname in flist ]

    with open(feats_fname_ordered, 'w') as f:
        for feat, fname in zip(feat_list_sorted, flist):
            f.write("%s#%s\n" % (feat, fname))

def hidost_feature(pdf_paths):
    if not os.path.isdir(cache_dir):
        os.system("mkdir -p %s" % (cache_dir))

    if not os.path.isfile(empty_file_list):
        os.system("touch %s" % (empty_file_list))
    
    sha1_str = hash_str(''.join(pdf_paths))
    tmp_dir = os.path.join(cache_dir, sha1_str)
    
    if os.path.isdir(tmp_dir):
        os.system("rm -rf %s" % tmp_dir)
    os.system("mkdir -p %s" % tmp_dir)
    
    pdf_file_list = os.path.join(tmp_dir, "input.pdfs.list")
    
    data_file = os.path.join(tmp_dir, "input.data.libsvm")
    data_file_corrected_order = os.path.join(tmp_dir, "input.data.ordered.libsvm")
    
    # cmd = "echo '%s' > %s " % ("", pdf_file_list)
    # os.system(cmd)

    # ---pdf-file-----> pdf2paths ---->  pdf-path-file
    for pdf_path in pdf_paths:
        #pdf_file_name = os.path.basename(pdf_path)
        pdf_file_name = hash_str(pdf_path) + ".pdf"

        cmd = "%s \"%s\" n > %s" % (pdf2paths_cmd, pdf_path, os.path.join(tmp_dir, pdf_file_name))
        #print cmd
        os.system(cmd)
        cmd = "echo '%s' >> %s " % (os.path.join(tmp_dir, pdf_file_name), pdf_file_list)
        os.system(cmd)

    # ----pdf-path-files----> feat-extract ------>  data.libsvm
    cmd = "%s -m %s -b %s -f %s -o %s" % (feat_extract_cmd, pdf_file_list, empty_file_list, feats_path, data_file)
    print(cmd)
    os.system(cmd)
    os.system("cat %s" % data_file)

    # Critical: the file order in input.pdfs.list may not be preserved in input.data.libsvm due to libquickly.
    correct_feats_order(data_file, pdf_file_list, data_file_corrected_order)

    #print 'Loading data file'
    X, _ = datasets.load_svmlight_file(data_file_corrected_order, 
                                       n_features=6087, 
                                       multilabel=False, 
                                       zero_based=False, 
                                       query_id=False)
    X = X.toarray()
    # os.system("rm -rf %s" % tmp_dir)
    return X

def get_feature_names(x):
    feat_id_list = x.nonzero()[0].tolist()
    return [feats[i] for i in feat_id_list]

def compare_feats(x1, x2):
    x1 = x1.nonzero()[0].tolist()
    x2 = x2.nonzero()[0].tolist()

    # deleted
    deleted = list(set(x1).difference(set(x2)))
    # added
    added = list(set(x2).difference(set(x1)))
    # fixed
    fixed = list(set(x2).intersection(set(x1)))

    return deleted, added, fixed

model = pickle.load(open(model_path, 'rb'))
def model_decision(X):
    y = model.decision_function(X)
    r = list(y)
    scores = [float(ele[0]) for ele in r]
    #os.system("rm -rf %s" % tmp_dir)
    return scores

def hidost(pdf_paths):
    X = hidost_feature(pdf_paths)
    return model_decision(X)

def hidost_feature_extractor(file_path):
    X = hidost_feature([file_path])
    feat = X[0].nonzero()[0].tolist()
    return feat

if __name__ == "__main__":
    if sys.argv[1] == 'feature':
        print hidost_feature_extractor(sys.argv[2])
    elif sys.argv[1] == 'compare':
        file1, file2 = sys.argv[2], sys.argv[3]
        X = hidost_feature([file1, file2])
        score1, score2 = model_decision(X)
        print "Scores: ", score1, score2
        deleted, added, fixed = compare_feats(X[0], X[1])
        if len(deleted) > 0:
            print "deleted: ", map(lambda x: feats[x], deleted)
        if len(added) > 0:
            print "added: ", map(lambda x: feats[x], added)

    else:
        pdf_list = sys.argv[1:]
        pdf_paths = map(os.path.abspath, pdf_list)

        results = hidost(pdf_paths)
        print results