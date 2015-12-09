import subprocess
import os
import sys
from lib.common import list_file_paths
import pickle

to_skip_pickle = "evade_both_to_skip.pickle"

if os.path.isfile(to_skip_pickle):
    to_skip = pickle.load(open(to_skip_pickle))
else:
    to_skip = []

def system_cmd(cmd):
    return subprocess.call(cmd.split(' '))

if __name__ == '__main__':
    seed_paths = list_file_paths('samples/seeds')

    if len(sys.argv) < 2:
        print "python batch.py [classifier_name] [ext_genome_folder] [round_id]"
        sys.exit(1)

    classifier_name = sys.argv[1]
    ext_genome_folder = sys.argv[2]
    ext_genome_tag = ext_genome_folder.split('/')[-1]
    round_id = int(sys.argv[3])
    token = "attack_%s_%s" % (classifier_name, ext_genome_tag)

    if not os.path.isdir(ext_genome_folder):
        print "Error: invalid ext genome folder."
        sys.exit(1)

    for seed_path in seed_paths[:]:
        start_hash = seed_path.split('/')[-1].split('.')[0]
        if start_hash in to_skip:
            print "Skipped ", start_hash
            continue
        cmd = "./gp.py -c %s -s %s -e %s -p 48 -g 20 -m 0.1 -x 0 -f 0 -t %s --round %d" \
              % (classifier_name, seed_path, ext_genome_folder, token, round_id)

        try:
            print cmd
            subprocess.call(cmd.split(' '))
        except KeyboardInterrupt, error:
            break
