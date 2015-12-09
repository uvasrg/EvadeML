import time
import os
import sys
import xml.etree.ElementTree as ET

_current_dir = os.path.abspath(os.path.dirname(__file__))
import_path = os.path.join(_current_dir, './wepawet')
sys.path.append(import_path)
from submit_to_wepawet import wepawet_submit_file, AnalysisOptions, wepawet_query

_current_dir = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.normpath(os.path.join(_current_dir, ".."))
sys.path.append(PROJECT_ROOT)

from lib.config import config
user = config.get('wepawet', 'username')
passwd = config.get('wepawet', 'password')

from lib.common import *
logger = logging.getLogger('gp.wepawet')

def submit_file(file_path):
    #resource = "./variants/test1.pdf"
    analysis_opts = AnalysisOptions()

    submit_status_xml = wepawet_submit_file(file_path, analysis_opts, user, passwd)
    #print submit_status_xml

    submit_status = ET.fromstring(submit_status_xml)
    task_id = None
    if submit_status.attrib['state'] == 'ok':
        if submit_status[0].tag == "hash":
           task_id = submit_status[0].text
    return task_id

# possible returns: error, benign, malicious
def query_task(task_id):
    ts = time.time()    
    status = "queued"
    result = "unknown"
    
    while status == "queued":
        try:
            #print "issue a query"
            task_report_xml = wepawet_query(task_id)
            #print task_report_xml
            task_report = ET.fromstring(task_report_xml)
            if task_report.attrib['state'] == 'ok':
                for child in task_report:
                    if child.tag == "status":
                        if child.text == "queued":
                            #print "queued, wait 2 secs"
                            time.sleep(3)
                            continue
                        status = child.text
                    if child.tag == 'result':
                        result = child.text
                        break
        except:
            print "error in task query, try again later"
            time.sleep(1)
            continue      
    return result

def judge_variant(file_path):
    task_id = submit_file(file_path)
    result = query_task(task_id)
    return result

# TODO: Submit files in multi threads.
# Done: don't submit file > 2MB
def submit_files(file_paths):
    task_ids = []
    for file_path in file_paths:
        task_id = ''
        
        fsize = os.path.getsize(file_path)
        if fsize >= 2*1024*1024:
            task_id = -1
        while task_id == '' or task_id == None:
            try:
                task_id = submit_file(file_path)
            except:
                print "Warning: Failed to get a task id in wepawet submission, retry 1 sec later."
                time.sleep(1)
        #results[file_path] = {}
        task_ids.append(task_id)
    return task_ids

def query_tasks(task_ids):
    results = []
    for task_id in task_ids:
        if task_id == -1:
            status = "error"
        else:
            status = query_task(task_id)
        results.append(status)
    return results

def judge_variants(file_paths):
    task_ids = []
    results = []
    for file_path in file_paths:
        task_id = ''
        while task_id == '' or task_id == None:
            try:
                task_id = submit_file(file_path)
            except:
                print "Warning: Failed to get a task id in wepawet submission, retry 1 sec later."
                time.sleep(1)
        #results[file_path] = {}
        task_ids.append(task_id)
        #results[file_path]['task_id'] = task_id
    
    #for file_path, status in results.items():
    #    status['result'] = query_task(status['task_id'])
    for task_id in task_ids:
        status = query_task(task_id)
        results.append(status)
    
    return results

def wepawet(file_paths):
    # submit files of unknown indices to wepawet
    logger.info("Submit %d files to wepawet." % len(file_paths))
    task_ids = wepawet.submit_files(file_paths)
    logger.info("Waiting for %d results from wepawet." % len(file_paths))
    query_results = wepawet.query_tasks(task_ids)
    logger.info("Finished.")
    return query_results

def test():
    file_paths = ['./samples/cv.pdf', './samples/OpenAction.pdf']
    print judge_variants(file_paths)

if __name__ == "__main__":
    sys.exit(test())
