#! /usr/bin/env python
import logging
import random
import pickle
import os
import sys
import getopt

from lib.common import LOW_SCORE, finished_flag, visited_flag, result_flag, error_flag
from lib.common import touch, deepcopy
from lib.common import setup_logging

# Import PDFRW later for controling the logging format.
# Note: The original pdfw should be used in parsing the repacked seeds for efficiency.
# No, we have to use the modified version, due to the additional trace issue.

class GPPdf:
    def __init__(self,
                 job_dir,
                 seed_sha1,
                 seed_file_path,
                 logger,
                 random_state_file_path,
                 ext_genome,
                 success_traces_path,
                 promising_traces_path,
                 gp_params,
                 fitness_function,
                 ):
        self.logger = logger
        self.job_dir = job_dir
        self.seed_sha1 = seed_sha1

        # Load the pre-defined random state for reproducing the existing results.
        if random_state_file_path:
            try:
                random_state = pickle.load(open(random_state_file_path, 'rb'))
                random.setstate(random_state)
                logger.debug("Loaded a random state from %s" % random_state_file_path)
            except:
                logger.warning("Failed to load random state from %s" % random_state_file_path)

        # Save random state for reproducing results in the future.
        random_state_file = os.path.join(self.job_dir, "random_state.pickle")
        random_state = random.getstate()
        pickle.dump(random_state, open(random_state_file, 'wb'))

        self.fitness_func = fitness_function

        # Load the seed.
        self.seed_file_path = seed_file_path
        self.seed_fitness = self.fitness([self.seed_file_path], self.seed_sha1)[0]
        self.seed_root = PdfGenome.load_genome(seed_file_path)
        self.logger.info("Loaded %s as PDF seed, fitness %.2f." % (seed_file_path, self.seed_fitness))

        # Load the external genome.
        self.ext_genome = ext_genome

        # Load traces.
        self.success_traces_path = success_traces_path
        self.success_traces = Trace.load_traces(self.success_traces_path)
        self.promising_traces_path = promising_traces_path
        self.promising_traces = Trace.load_traces(self.promising_traces_path)

        # Initiate some parameters.
        self.gp_params = gp_params
        self.pop_size = gp_params['pop_size']
        self.max_gen = gp_params['max_gen']
        self.mut_rate = gp_params['mut_rate']
        self.xover_rate = gp_params['xover_rate']
        self.fitness_threshold = gp_params['fitness_threshold']        

    def save_variants_to_files(self):
        folder = "./variants/generation_%d" % (self.generation)
        folder = os.path.join(self.job_dir, folder)
        if not os.path.isdir(folder):
            os.makedirs(folder)
        file_paths = []
        for j in range(len(self.popul)):
            path = "./variants/generation_%d/%d.pdf" % (self.generation, j)
            path = os.path.join(self.job_dir, path)
            file_paths.append(path)
            PdfGenome.save_to_file(self.popul[j], path)
        return file_paths

    def load_variant(self, gen, vid):
        path = "./variants/generation_%d/%d.pdf" % (gen, vid)
        path = os.path.join(self.job_dir, path)
        pdf_obj = PdfGenome.load_genome(path)
        return pdf_obj

    def load_variant_trace(self, gen, vid):
        path = "./variants/generation_%d/%d.pdf" % (gen, vid)
        path = os.path.join(self.job_dir, path)
        trace = PdfGenome.load_trace(path)
        return trace

    def fitness(self, *args):
        return self.fitness_func(*args)

    def run(self):
        self.logger.info("Start a gp task with %s" % (self.gp_params))
        
        score_file_name = os.path.join(self.job_dir, "fitness_scores.pickle")
        self.fitness_scores = {}
        
        self.popul = self.initial_population()
        self.generation = 1

        while self.generation <= self.max_gen:
            self.logger.info("There're %d variants in population at generation %d." % (len(self.popul), self.generation))

            file_paths = self.save_variants_to_files()

            scores = self.fitness(file_paths, self.seed_sha1)
            # Introduce a fake score for testing tracing.
            # scores = [0.1, 0.2] * (self.pop_size/2)

            self.fitness_scores[self.generation] = scores
            pickle.dump(self.fitness_scores, open(score_file_name, 'wb'))
            
            self.logger.info("Fitness scores: %s" % scores)
            self.logger.info("Sorted fitness: %s" % sorted(scores, reverse=True))
            
            if max(scores) > self.fitness_threshold:
                self.best_score = max(scores)
                self.logger.info("Already got a high score [%.2f]>%.2f variant, break the GP process." % (max(scores), self.fitness_threshold))
                
                # Store the success traces.
                for i in range(len(scores)):
                    score = scores[i]
                    if score > self.fitness_threshold:
                        success_trace = self.popul[i].active_trace
                        self.success_traces.append(success_trace)

                # Dump the new generated traces.
                # We assume no concurrent GP tasks depending on the traces.
                Trace.dump_traces(self.success_traces, self.success_traces_path)
                touch(os.path.join(self.job_dir, finished_flag))
                break
            elif self.generation == max_gen:
                self.logger.info("Failed at max generation.")
                if max(scores) >= self.seed_fitness:
                    best_gen, best_vid, self.best_score = self.get_best_variant(1, self.generation)
                    promising_trace = self.load_variant_trace(best_gen, best_vid)

                    self.logger.info("Save the promising trace %.2f of %d:%d" % (best_score, best_gen, best_vid))

                    self.promising_traces.append(promising_trace)
                    Trace.dump_traces(self.promising_traces, self.promising_traces_path, exclude_traces=self.success_traces)
                break

            # Crossover
            if self.xover_rate > 0:
                self.popul = self.select(self.popul, scores, self.pop_size/2)
                self.logger.debug("After selecting goods and replacing bads, we have %d variants in population." % len(self.popul))

                for p1,p2 in zip(self.popul[0::2], self.popul[1::2]):
                    c1, c2 = PdfGenome.crossover(p1, p2)
                    self.popul.append(c1)
                    self.popul.append(c2)
                self.logger.debug("After crossover, we have %d variants in population." % len(self.popul))
            else: # No Crossover
                self.popul = self.select(self.popul, scores, self.pop_size)
                self.logger.debug("After selecting goods and replacing bads, we have %d variants in population." % len(self.popul))

            # Mutation
            for i in range(len(self.popul)):
                if i not in self.vid_from_trace:
                    self.logger.debug("Generating %d:%d variant" % (self.generation+1, i))
                    self.popul[i] = PdfGenome.mutation(self.popul[i], self.mut_rate, self.ext_genome)
                else:
                    self.logger.debug("Keep %d:%d variant from trace." % (self.generation+1, i))

            self.generation = self.generation + 1

        self.logger.info("Stopped the GP process with max fitness %.2f." % self.best_score)
        touch(os.path.join(self.job_dir, result_flag % self.best_score))
        return True

    def initial_population(self):
        logger = self.logger
        logger.info("Getting initial population from existing mutation traces (success: %d, promising: %d)." \
                    % (len(self.success_traces), len(self.promising_traces)))
        popul = []

        traces = self.success_traces + self.promising_traces
        traces = Trace.get_distinct_traces(traces)
        logger.info("Got %d distinct traces" % len(traces))
        self.traces = traces

        self.remaining_traces_id = range(len(traces))

        if 0 < len(self.remaining_traces_id) <= self.pop_size:
            tid_picked = self.remaining_traces_id
        elif len(self.remaining_traces_id) > self.pop_size:
            tid_picked = random.sample(self.remaining_traces_id, self.pop_size)
            tid_picked.sort()
        else:
            tid_picked = []

        # generate_variants_from_traces
        for i in tid_picked:
            self.remaining_traces_id.remove(i)
            logger.debug("Generating %d variant from existing trace." % i)
            trace = traces[i]
            variant_root = Trace.generate_variant_from_trace(self.seed_root, trace, self.ext_genome)
            popul.append(variant_root)

        if len(popul) < int(self.pop_size):
            logger.info("Getting %d more variants in initial population by random mutation." \
                        % (int(self.pop_size) - len(popul)))

        while len(popul) < int(self.pop_size):
            i = len(popul)
            logger.debug("Getting variant %d in initial population." % i)
            root = deepcopy(self.seed_root)
            root = PdfGenome.mutation(root, self.mut_rate, self.ext_genome)
            popul.append(root)
        return popul

    def get_best_variant(self, start_gen, end_gen):
        best_gen = 1
        best_vid = 0
        best_score = LOW_SCORE
        for gen in range(start_gen, end_gen+1):
            scores = self.fitness_scores[gen]
            if max(scores) > best_score:
                best_score = max(scores)
                best_gen = gen
                best_vid = scores.index(best_score)
        return best_gen, best_vid, best_score

    def select(self, orig_list, scores, sel_size):
        # when reverse==False, select variants with lower score, otherwise select higher scores.
        sorted_indices = [i[0] for i in sorted(enumerate(scores), key=lambda x:x[1], reverse=True)]
        
        ret = []
        self.vid_from_trace = []
        
        for i in sorted_indices[:sel_size]:
            if scores[i] == LOW_SCORE:
                if len(self.remaining_traces_id) > 0:
                    # TODO: need to label these, not to mutate in next generation.
                    self.vid_from_trace.append(i)
                    tid_picked = random.choice(self.remaining_traces_id)
                    self.remaining_traces_id.remove(tid_picked)
                    self.logger.info("Ignored a variant with low score, generating from existing trace %d" % tid_picked)
                    trace = self.traces[tid_picked]
                    new_variant = Trace.generate_variant_from_trace(self.seed_root, trace, self.ext_genome)
                    ret.append(new_variant)

                elif self.generation == 1:
                    self.logger.info("Ignored a variant with low score, replace with original seed.")
                    ret.append(deepcopy(self.seed_root))
                else:
                    choice = random.choice(['seed', 'last_gen_best', 'historic_best'])
                    if choice == "seed":
                        self.logger.info("Ignored a variant with low score, replace with original seed.")
                        ret.append(deepcopy(self.seed_root))
                    elif choice == "last_gen_best":
                        best_gen, best_vid, best_score = self.get_best_variant(self.generation-1, self.generation-1)
                        best_root =  self.load_variant(best_gen, best_vid)
                        ret.append(best_root)
                        self.logger.info("Ignored a variant with low score, replace with best variant in last generation[%d, %d]." % (best_gen, best_vid))
                    elif choice == "historic_best":
                        best_gen, best_vid, best_score = self.get_best_variant(1, self.generation-1)
                        best_root =  self.load_variant(best_gen, best_vid)
                        ret.append(best_root)
                        self.logger.info("Ignored a variant with low score, replace with best variant in historic generation[%d, %d]." % (best_gen, best_vid))
            else:
                self.logger.info("Selected a file with score %.2f" % scores[i])
                ret.append(orig_list[i])
        
        return ret

def get_opt(argv):
    classifier_name = None
    start_file = None
    ext_genome_folder = None
    pop_size = None
    max_gen = None
    mut_rate = None
    xover_rate = 0
    stop_fitness = None
    random_state_file_path = None
    token = None
    round_id = 1

    help_msg = "gp.py -c <classifier name> -o <oracle name> \
        -s <start file location> -e <external genome folder> \
        -p <population size> -g <max generation> \-m <mutation rate> \
        -x <crossvoer rate> -r <random_state_file_path> -t <task_token>\
        --round <round_id>\
        -f <stop criterion in fitness score>"
    
    if len(argv) < 2:
        print help_msg
        sys.exit(2)

    try:
        opts, args = getopt.getopt(argv[1:],"hc:s:e:p:g:m:f:x:r:t:",["classifier=",
                                                                 "sfile=",
                                                                 "extgenome=",
                                                                 "popu=",
                                                                 "gen=",
                                                                 "mut=",
                                                                 "fitness=",
                                                                 "crossover=",
                                                                 "random_state=",
                                                                 "token=",
                                                                 "round=",
                                                                 ])
    except getopt.GetoptError:
        print help_msg
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print help_msg
            sys.exit()
        elif opt in ("-c", "--classifier"):
            classifier_name = arg
        elif opt in ("-s", "--sfile"):
            start_file = arg
        elif opt in ("-e", "--extgenome"):
            ext_genome_folder = arg
        elif opt in ("-p", "--popu"):
            pop_size = int(arg)
        elif opt in ("-g", "--gen"):
            max_gen = int(arg)
        elif opt in ("-m", "--mut"):
            mut_rate = float(arg)
        elif opt in ("-x", "--crossover"):
            xover_rate = float(arg)
        elif opt in ("-f", "--fitness"):
            stop_fitness = float(arg)
        elif opt in ("-r", "--random_state"):
            random_state_file_path = arg
        elif opt in ("-t", "--token"):
            token = arg
        elif opt in("--round"):
            round_id = int(arg)
    
    if xover_rate != 0 and pop_size % 4 != 0:
        print "The population size should be times of 4."
        sys.exit(2)

    print classifier_name, start_file, ext_genome_folder, \
        pop_size, max_gen, mut_rate, xover_rate, \
        stop_fitness, random_state_file_path, token, round_id

    return classifier_name, start_file, ext_genome_folder, \
        pop_size, max_gen, mut_rate, xover_rate, \
        stop_fitness, random_state_file_path, token, round_id

if __name__ == "__main__":
    classifier_name, start_file_path, \
        ext_genome_folder, pop_size, max_gen, mut_rate, \
        xover_rate, stop_fitness, random_state_file_path, \
        task_token, round_id = get_opt(sys.argv)

    start_hash = os.path.basename(start_file_path).split('.')[0]

    for rid in range(1, round_id + 1):
        job_dir = "./results/%s/log_r%d/classifier=%s,mut=%.1f,xover=%.1f,popsz=%d,maxgen=%d,stopfit=%.2f,start=%s" \
                    % (task_token, rid, classifier_name, mut_rate, xover_rate, pop_size, max_gen, stop_fitness, start_hash)
        if not os.path.isdir(job_dir):
            os.makedirs(job_dir)

        # skip the succeeded tasks in previous rounds.
        # skip all the visited tasks in the current round.
        if os.path.exists(os.path.join(job_dir, finished_flag)):
            sys.exit(0)
        if rid == round_id and os.path.exists(os.path.join(job_dir, visited_flag)):
            sys.exit(0)

    traces_dir = "./results/%s/trace/" % task_token
    if not os.path.isdir(traces_dir):
        os.makedirs(traces_dir)
    success_traces_path = traces_dir + "success_traces.pickle"
    promising_traces_path = traces_dir + "promising_traces.pickle"

    log_file_path = os.path.join(job_dir, visited_flag)
    setup_logging(log_file_path)
    logger = logging.getLogger('gp.core')
    logger.info("Starting logging for a GP process...")

    # Due to logging is called in pdfrw, they have to be imported after basicConfig of logging.
    # Otherwise, the above basicConfig would be overridden.
    from lib.pdf_genome import PdfGenome
    from lib.trace import Trace

    if classifier_name == 'pdfrate':
        from lib.fitness import fitness_pdfrate as fitness_func
    elif classifier_name == 'hidost':
        from lib.fitness import fitness_hidost as fitness_func
    elif classifier_name == "hidost_pdfrate":
        from lib.fitness import fitness_hidost_pdfrate as fitness_func
    elif classifier_name == "hidost_pdfrate_mean":
        from lib.fitness import fitness_hidost_pdfrate_mean as fitness_func
    elif classifier_name == "hidost_pdfrate_sigmoid":
        from lib.fitness import fitness_hidost_pdfrate_sigmoid as fitness_func

    gp_params = {'pop_size': pop_size, 'max_gen': max_gen, \
             'mut_rate': mut_rate, 'xover_rate': xover_rate, \
             'fitness_threshold': stop_fitness}
    ext_genome = PdfGenome.load_external_genome(ext_genome_folder)

    try:
        gp = GPPdf( job_dir = job_dir,
                    seed_sha1 = start_hash,
                    seed_file_path = start_file_path,
                    logger = logger,
                    random_state_file_path = random_state_file_path,
                    ext_genome = ext_genome,
                    success_traces_path = success_traces_path,
                    promising_traces_path = promising_traces_path,
                    gp_params = gp_params,
                    fitness_function = fitness_func,
                    )
        gp.run()
    except Exception, e:
        touch(os.path.join(job_dir, error_flag))
        logger.exception(e)
        sys.exit(1)
