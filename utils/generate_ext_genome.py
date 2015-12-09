#! /usr/bin/env python

import sys
import pickle
import os
import shutil

_current_dir = os.path.abspath(os.path.dirname(__file__))
import_path = os.path.join(_current_dir, '..')
sys.path.append(import_path)

from lib.common import list_file_paths
from lib.pdf_genome import PdfGenome
from lib.detector import query_classifier

class ExtGenome:
    def __init__(self, classifier_name, folder, file_number):
        self.classifier_func = lambda *args:query_classifier(classifier_name, *args)
        self.folder = folder
        self.fpaths = list_file_paths(self.folder)
        self.file_number = file_number

    def classifier(self, *args):
        return self.classifier_func(*args)

    def path_count(self, file_paths):
        ret = []
        for fpath in file_paths:
            pdf_obj = PdfGenome.load_genome(fpath)
            paths = PdfGenome.get_object_paths(pdf_obj)
            ret.append(len(paths))
        return ret

    # Note: I don't think the score of externals is that important. What really matters is the diversity of the structure.
    def select_files(self):
        file_paths = self.fpaths
        limit = self.file_number
        classifier_results = self.classifier(file_paths)
        path_count = self.path_count(file_paths)
        file_size = map(os.path.getsize, file_paths)
        file_size = map(lambda x:x/float(1024), file_size)

        chose_idx = sorted(range(len(classifier_results)), key=lambda i: (classifier_results[i], file_size[i]))

        for idx in chose_idx:
            print ("Score: %.2f, Path_count: %d, File_size: %.1f KB, Name: %s" % (classifier_results[idx], path_count[idx], file_size[idx], os.path.basename(file_paths[idx])))

        chose_idx = chose_idx[:limit]
        print ("Chose %d external files." % (limit))

        file_paths_sub = [file_paths[i] for i in chose_idx]
        return file_paths_sub

    def load_external_genome(self, file_paths):
        ext_pdf_paths = [] # element: (entry, path)
        self.genome_desc = []
        for file_path in file_paths:
            pdf_obj = PdfGenome.load_genome(file_path)
            paths = PdfGenome.get_object_paths(pdf_obj)
            for path in paths:
                ext_pdf_paths.append((pdf_obj, path))
            self.genome_desc.append((file_path, len(path)))
        return ext_pdf_paths

    @staticmethod
    def copy_file_to_folders(flist, tgt_folder):
        if not os.path.isdir(tgt_folder):
            os.makedirs(tgt_folder)
        for fpath in flist:
            shutil.copy2(fpath, tgt_folder)

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print "./%s [classifier_name] [sample_folder] [file_number]" % (sys.argv[0])

    classifier_name, sample_folder, file_limit = sys.argv[1:4]
    file_limit = int(file_limit)
        
    ext_genome_folder = os.path.join(_current_dir, "../samples/ext_genome/%s_%d_new" % (classifier_name, file_limit))
    ext_genome_folder = os.path.abspath(ext_genome_folder)
    
    pdf_geno = ExtGenome(classifier_name, sample_folder, file_limit)
    selected_files = pdf_geno.select_files()

    answer = raw_input("Do you want to copy the %d selected files to %s? [y/N]" % (len(selected_files), ext_genome_folder))
    if answer == 'y':
        ExtGenome.copy_file_to_folders(selected_files, ext_genome_folder)