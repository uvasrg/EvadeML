#! /usr/bin/env python

# Server side
# Input: a list of file paths for examing
# 1. Look up all the files in cache db by sha1 string
# 2. If there're unknown samples, submit to wepawet, fetch the results after a long waiting, then save to local cache db. (rwlock protected variable)
# 3. Fetch the results from local cache, and return to client.
# Problem: 
# Return: a list of wepawet (or local classifier) results.

# TODO: Ctrl-C doesn't work well.

from SocketServer import ThreadingMixIn
from SimpleXMLRPCServer import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler
import threading
import time
import pickle
import os
import sys

# Make sure the working directory in the src.
_current_dir = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.normpath(os.path.join(_current_dir, ".."))
sys.path.append(PROJECT_ROOT)

from lib.config import config
HOST = config.get('detector_agent', 'host')
PORT = int(config.get('detector_agent', 'port'))

from lib.common import hash_file

# Import local classifiers.
from classifiers.pdfrate_wrapper import pdfrate
from classifiers.hidost_wrapper import hidost
from classifiers.bundle_wrapper import hidost_pdfrate, hidost_pdfrate_sigmoid

import sklearn
print sklearn.__version__

# Import remote classifiers.
from classifiers.cuckoo_wrapper import cuckoo
from classifiers.wepawet_wrapper import wepawet

from mongo_cache import query_classifier_cache, insert_classifier_cache

import logging
logger = logging.getLogger("DAgent-dev")

#Threaded XML-RPC
class XMLRPCServerT(ThreadingMixIn, SimpleXMLRPCServer): pass

# A cached and general query function.
def query(file_paths, real_query_method=None, query_method=None, insert_method=None, expected_sig=None):
    hash_strs = map(hash_file, file_paths)
    results = map(query_method, hash_strs)
    logger.info("(%d unique) files" % (len(set(hash_strs))))

    unknown_samples_count = results.count(None)
    logger.info("%d files hit in cache.  " % (len(file_paths) - unknown_samples_count))
    if unknown_samples_count == 0:
        return results

    unknown_indices = [i for i, j in enumerate(results) if j == None]

    query_files = {}
    to_wpw_files = []
    hashes = []

    for idx in unknown_indices:
        hash_str = hash_strs[idx]
        if not query_files.has_key(hash_str):
            query_files[hash_str] = [idx]
            to_wpw_files.append(file_paths[idx])
            hashes.append(hash_str)
        else:
            query_files[hash_str].append(idx)
            
    # submit files of unknown indices to wepawet
    logger.info("Waiting for %d results." % len(file_paths))
    query_results = real_query_method(to_wpw_files)
    logger.info("Finished.")

    for i in range(len(hashes)):
        hash_str = hashes[i]
        result = query_results[i]

        insert_method(hash_str, result, expected_sig)
        for idx in query_files[hash_str]:
            results[idx] = result

    return results

def query_classifier(classifier_name, file_paths, seed_sha1 = None):
    expected_sig = None
    logger.info("Received %s query for %d files" % (classifier_name, len(file_paths)))

    query_method = lambda x:query_classifier_cache(classifier_name, x)
    insert_method = lambda *args:insert_classifier_cache(classifier_name, *args)

    if classifier_name == "pdfrate":
        real_query_method = pdfrate
    elif classifier_name == "hidost":
        real_query_method = hidost
    elif classifier_name == "wepawet":
        real_query_method = wepawet
    elif classifier_name == "cuckoo":
        real_query_method = cuckoo
        print "seed_sha1:", seed_sha1
        expected_sig = cuckoo_seed_sigs[seed_sha1]
    elif classifier_name == "hidost_pdfrate":
        real_query_method = hidost_pdfrate
    elif classifier_name == "hidost_pdfrate_sigmoid":
        real_query_method = hidost_pdfrate_sigmoid
    else:
        print "Unknown classifier: %s" % classifier_name
        return None

    results = query(file_paths, real_query_method=real_query_method, \
                     query_method=query_method, insert_method=insert_method, expected_sig=expected_sig)
    assert(len(file_paths) == len(results))

    if classifier_name == "cuckoo":
        bin_ret = ['malicious' if sig == expected_sig else 'benign' for sig in results]
        return bin_ret
    else:
        return results

if __name__ == "__main__":
    cuckoo_sig_pickle = sys.argv[1]
    cuckoo_seed_sigs = pickle.load(open(cuckoo_sig_pickle))

    log_file_path = os.path.join(_current_dir, "dagent_server.log")
    logging.basicConfig(filename=log_file_path,
                            filemode='a',
                            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                            level=logging.INFO)
    logger = logging.getLogger("DAgent")
    logger.info("Starting DAgent service...")
    
    server = XMLRPCServerT((HOST, PORT), SimpleXMLRPCRequestHandler)
    server.register_function(query_classifier, "query_classifier")
    print "Server is ready at http://%s:%d" % (HOST, PORT)
    server.serve_forever()
