import pickle
from common import *
from pdf_genome import PdfGenome

logger = logging.getLogger('gp.trace')

class Trace:
    def __init__(self):
        pass

    @staticmethod
    def load_traces(pickle_path):
        if os.path.isfile(pickle_path):
            traces = pickle.load(open(pickle_path, 'rb'))
            return traces
        else:
            return []

    @staticmethod
    def dump_traces(traces, pickle_path, exclude_traces = None):
        traces = Trace.get_distinct_traces(traces, exclude_traces = exclude_traces)
        pickle.dump(traces, open(pickle_path, 'wb'))

    # Only need to run at once: at loading or restoring.
    @staticmethod
    def get_distinct_traces(traces, exclude_traces = None):
        uniques = []
        str_set = set()
        if exclude_traces:
            exclude_str_set = set([str(trace) for trace in exclude_traces])
        else:
            exclude_str_set = set()
        for trace in traces:
            trace_str = str(trace)
            if trace_str not in str_set and trace_str not in exclude_str_set:
                uniques.append(trace)
                str_set.add(str(trace))
        return uniques

    @staticmethod
    def generate_variant_from_trace(seed_root, trace, ext_genome):
        root = deepcopy(seed_root)
        trace = deepcopy(trace)
        Trace.execute_mut_trace(root, trace, ext_genome)
        root.private.active_trace = trace
        return root

    @staticmethod
    def execute_mut_trace(root, trace, ext_genome):
        for operation in trace:
            op, op_obj_path, ext_id = operation
            ext_root, tgt_obj_path = ext_genome[ext_id]

            try:
                if op == 'delete':
                    PdfGenome.delete(root, op_obj_path)
                elif op == 'insert':
                    PdfGenome.insert(root, op_obj_path, ext_root, tgt_obj_path)
                elif op == 'swap':
                    PdfGenome.swap(root, op_obj_path, ext_root, tgt_obj_path)
                else:
                    logger.error("undefined operator: ", op)
            except:
                logger.error("operation failed: %s" % str(operation))
        return root

def _generate_variant_from_trace(ntuple):
    return Trace.generate_variant_from_trace(*ntuple)