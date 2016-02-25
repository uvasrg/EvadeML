import os
import copy
import hashlib
import logging

def setup_logging(log_file_path):
    logging.basicConfig(filename=log_file_path,
                        filemode='a',
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.DEBUG,
                        )

LOW_SCORE = -65535

finished_flag = "evaded.flag"
visited_flag = "dev.log"
result_flag = "fitness_%.2f.flag"
error_flag = "error.flag"

# Make the order of file list deterministic.
def list_file_paths(dir_name, size_limit=None):
    fnames = os.listdir(dir_name)
    fnames.sort()

    ret = [os.path.join(dir_name, fname) for fname in fnames]
    if size_limit:
        return ret[:size_limit]
    else:
        return ret

def touch(fname):
    try:
        os.utime(fname, None)
    except:
        open(fname, 'a').close()

def deepcopy(obj):
    return copy.deepcopy(obj)

def hash_file(filepath):
    sha1 = hashlib.sha1()
    f = open(filepath, 'rb')
    try:
        sha1.update(f.read())
    finally:
        f.close()
    return sha1.hexdigest()


