from common import *
import pickle
import random

import pdfrw
from pdfrw import PdfReader, PdfWriter
from pdfrw.objects import PdfDict, PdfArray, PdfName, PdfObject, PdfIndirect

logger = logging.getLogger('gp.pdf_genome')


class PdfGenome:
    def __init__(self):
        pass

    @staticmethod
    def load_genome(pdf_file_path, pickleable = False):
        pdf_obj = PdfReader(pdf_file_path, slow_parsing=False)

        if pickleable:
            # Remove the dynamic contents to make it pickleable.
            PdfGenome.save_to_file(pdf_obj, os.devnull)
            del pdf_obj.source
        return pdf_obj

    @staticmethod
    def save_to_file(pdf_obj, file_path):
        short_path_for_logging = '/'.join(file_path.split('/')[-3:])
        logger.debug("Saving to file: " + short_path_for_logging)
        y = PdfWriter()
        y.write(file_path, pdf_obj)
        logger.debug("Done")

    @staticmethod
    def load_trace(pdf_file_path):
        fpath = pdf_file_path + ".trace"
        if os.path.isfile(fpath):
            f = open(fpath, 'rb')
            trace = pickle.load(f)
            return trace
        else:
            return None

    @staticmethod
    def load_external_genome(folder, pickleable = False):
        ext_pdf_paths = [] # element: (entry, path)
        for file_path in list_file_paths(folder):
            pdf_obj = PdfGenome.load_genome(file_path, pickleable)
            paths = PdfGenome.get_object_paths(pdf_obj)
            for path in paths:
                ext_pdf_paths.append((pdf_obj, path))
        return ext_pdf_paths

    @staticmethod
    def get_object_paths(entry, exclude_paths = set()):
        logger.debug("Fetch object paths from an entry.")

        group_types = [pdfrw.pdfreader.PdfReader, pdfrw.objects.pdfdict.PdfDict, pdfrw.objects.pdfarray.PdfArray]
        if entry.Root == None:
            logger.warning("No /Root. in %s " % entry.keys())
            entry.Root = pdfrw.objects.pdfdict.PdfDict()
            return []
        obj_queue = entry.Root.items() # queue for tree node traversal, (path, obj) pairs

        # Track the visited objs during traversal, actually only PdfArray and PdfDict
        visited_objs_paths = {}
        paths_collection = []

        while len(obj_queue)>0:
            (path, obj) = obj_queue.pop(0)
            if type(path) != list:
                path = ['/Root', path]
            if pickle.dumps(path) in exclude_paths:
                continue
            if type(obj) not in group_types:
                # Terminal nodes, no need to expand, so directly add to the returned list of paths.
                paths_collection.append(path)
            else:
                # Non-terminal nodes. Need further traversal.
                obj_id = id(obj)
                if visited_objs_paths.has_key(obj_id):
                    #paths_collection.append(path) # Why should we add a visited obj?
                    visited_objs_paths[obj_id].append(path)
                    continue
                visited_objs_paths[obj_id] = [path]
                paths_collection.append(path)
                
                try:
                    references = obj.keys()
                except AttributeError:
                    references = range(len(obj))
                for reference in references:
                    child_obj = obj[reference]
                    new_path = path[:]
                    new_path.append(reference)
                    obj_queue.append((new_path, child_obj))

        logger.debug("Fetch %d object paths." % len(paths_collection))
        return paths_collection

    @staticmethod
    def get_parent_key(entry, path):
        parent = entry
        for key in path[:-1]:
            parent = parent[key]
        key = path[-1]
        return parent, key

    @staticmethod
    def delete(entry, path):
        logger.debug("###delete %s" % (path))
        parent, key = PdfGenome.get_parent_key(entry, path)
        if isinstance(parent, list):
            if key >= len(parent):
                logger.error("Cannot delete invalid index in PdfArray: %s" % path)
                return False
        elif isinstance(parent, dict):
            if not parent.has_key(key):
                logger.error("Cannot delete invalid key in PdfDict: %s" % path)
                return False
        else:
            logger.error("The parent node is not PdfArray or PdfDict, but %s!" % type(parent))

        if isinstance(parent, dict):
            parent[key] = None
        elif type(key) == int and isinstance(parent, list):
            del parent[key]
        else:
            # TODO: ERROR:GPPdf:The key is not a string or integer but <class 'pdfrw.objects.pdfobject.PdfObject'>: /Filter
            logger.error("The key is not a string or integer but %s: %s" % (type(key), key))
            return False
        return True

    @staticmethod
    def swap(src_entry, src_path, tgt_entry, tgt_path):
        logger.debug("###swap %s and %s" % (str(src_path), str(tgt_path)))

        src_parent, src_key = PdfGenome.get_parent_key(src_entry, src_path)
        src_obj = src_parent[src_key]

        tgt_parent, tgt_key = PdfGenome.get_parent_key(tgt_entry, tgt_path)
        tgt_obj = tgt_parent[tgt_key]

        tgt_obj = deepcopy(tgt_obj)
        src_parent[src_key] = tgt_obj
        return True

    @staticmethod
    def insert(src_entry, src_path, tgt_entry, tgt_path):
        logger.debug("###insert %s after %s" % (str(tgt_path), str(src_path)))
        
        src_parent, src_key = PdfGenome.get_parent_key(src_entry, src_path)
        src_obj = src_parent[src_key]

        tgt_parent, tgt_key = PdfGenome.get_parent_key(tgt_entry, tgt_path)
        tgt_obj = tgt_parent[tgt_key]

        if not src_entry is tgt_entry:
            # TODO: RuntimeError: maximum recursion depth exceeded in cmp
            tgt_obj = deepcopy(tgt_obj)

        if isinstance(src_parent, list):
            src_parent.insert(src_key+1, tgt_obj)
        elif isinstance(src_parent, dict):
            # Same: ['/Size'], [PdfObject("/Size")]
            real_key = str(tgt_key) # it can be an integer.
            if "/" not in real_key:
                real_key = PdfObject("/"+real_key)
            src_parent[real_key] = tgt_obj
        
        return True

    @staticmethod
    def mutation(entry, mut_prob, ext_genome, clone = False):
        if not entry:
            return False
        if clone == True:
            entry = deepcopy(entry)

        # visited path in string, updated after each mutation on node
        visited_paths = set()
        remaining_paths = list()
        remaining_paths = PdfGenome.get_object_paths(entry, visited_paths)
        trace = []

        ops = ['insert', 'swap', 'delete']
        
        # TODO: replaced with a collection of visited path for determining next node that should visit. (breadth-first traversal)
        while len(remaining_paths) > 0:
            op_obj_path = remaining_paths.pop(0)
            visited_paths.add(pickle.dumps(op_obj_path))
            if random.uniform(0,1) <= mut_prob:
                op = random.choice(ops)
                ext_id = random.choice(range(len(ext_genome)))
                operation = (op, op_obj_path, ext_id)
                trace.append(operation)
                logger.debug("Perform %s" % str(operation))

                tgt_entry, tgt_obj_path = ext_genome[ext_id]

                if op == 'delete':
                    PdfGenome.delete(entry, op_obj_path)
                elif op == 'insert':
                    PdfGenome.insert(entry, op_obj_path, tgt_entry, tgt_obj_path)
                elif op == 'swap':
                    PdfGenome.swap(entry, op_obj_path, tgt_entry, tgt_obj_path)
                else:
                    logger.error("undefined operator: ", op)

                remaining_paths = PdfGenome.get_object_paths(entry, visited_paths)
        if entry.active_trace == None:
            entry.private.active_trace = trace
        else:
            entry.active_trace.extend(trace)
        return entry

    @staticmethod
    def get_crossover_point(entry):
        obj_paths = PdfGenome.get_object_paths(entry)
        if len(obj_paths) > 0:
            return random.choice(obj_paths)
        else:
            return None

    @staticmethod
    def crossover(entry_a, entry_b):
        c1 = deepcopy(entry_a)
        c2 = deepcopy(entry_b)

        path_a = PdfGenome.get_crossover_point(c1)
        path_b = PdfGenome.get_crossover_point(c2)
        
        if not path_a or not path_b:
            logger.error("###crossover failed due to null variant.")
            return c1, c2

        logger.debug("###crossover between %s and %s" % (str(path_a), str(path_b)))

        parent_a, key_a = PdfGenome.get_parent_key(c1, path_a)
        parent_b, key_b = PdfGenome.get_parent_key(c2, path_b)

        obj_a = parent_a[key_a]
        obj_b = parent_b[key_b]

        parent_a[key_a] = obj_b
        parent_b[key_b] = obj_a
        return c1, c2

# Parameters in a tuple.
def _mutation(ntuples):
    return PdfGenome.mutation(*ntuples)

# Test: A multiprocessing method with no requirement for pickable pdfrw objects.
def _mutation_on_file(ntuples):
    src_path, dst_path, mut_prob, ext_folder = ntuples
    pdf_obj = PdfGenome.load_genome(src_path)
    ext_genome = PdfGenome.load_external_genome(ext_folder)
    mutated_pdf_obj = PdfGenome.mutation(pdf_obj, mut_prob, ext_genome)
    PdfGenome.save_to_file(mutated_pdf_obj, dst_path)
    return True

