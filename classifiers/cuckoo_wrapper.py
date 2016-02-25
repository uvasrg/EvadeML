import os
import requests
import json
import sys
import hashlib
import time
import re

_current_dir = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.normpath(os.path.join(_current_dir, ".."))
sys.path.append(PROJECT_ROOT)

from lib.config import config
HOST = config.get('cuckoo', 'host')
PORT = int(config.get('cuckoo', 'port'))
TIMEOUT = int(config.get('cuckoo', 'timeout'))

from lib.common import *
logger = logging.getLogger('gp.cuckoo')

def check_reported(file_path):
    sha1 = hash_file(file_path)
    REST_URL = "http://%s:%d/tasks/check_reported/%s" % (HOST, PORT, sha1)
    request = requests.get(REST_URL)
    if request.status_code == 200:
        json_decoder = json.JSONDecoder()
        if request.text:
            r = json_decoder.decode(request.text)
            return r

def submit(file_path, public_name = None, timeout = None, cache=False):
    if cache:
        task_id = check_reported(file_path)
        if task_id:
            #print "skip one file to submit", file_path
            return task_id
    #print "submit one file", file_path
    REST_URL = "http://%s:%d/tasks/create/file" % (HOST, PORT)
    with open(file_path, "rb") as sample:
        if not public_name:
            public_name = os.path.basename(file_path)
        multipart_file = {"file": (public_name, sample)}

        args = {}
        if timeout:
            args['timeout'] = timeout
        if cache != True:
            args['cache'] = cache
        if args != {}:
            request = requests.post(REST_URL, files=multipart_file, data=args)
        else:
            request = requests.post(REST_URL, files=multipart_file)

    # Add your code to error checking for request.status_code.
    print "request.status_code:", type(request.status_code), request.status_code
    if request.status_code == 200:
        json_decoder = json.JSONDecoder()
        task_id = json_decoder.decode(request.text)["task_id"]
        print "task_id:", type(task_id), task_id
        return task_id
    # Add your code for error checking if task_id is None.

def submit_files(file_paths, timeout=None, cache=False):
    task_ids = []
    for file_path in file_paths:
        print file_path
        task_id = None
        while task_id == None:
            task_id = submit(file_path, public_name=None, timeout=timeout, cache=cache)
        task_ids.append(task_id)
    return task_ids

# "pending", "running", "reported", "finished", "failed_analysis"
def view(task_id):
    REST_URL = "http://%s:%d/tasks/view/%d" % (HOST, PORT, task_id)
    request = requests.get(REST_URL)
    if request.status_code == 200:
        json_decoder = json.JSONDecoder()
        status = json_decoder.decode(request.text)["task"]["status"]
        return status

def delete_task(task_id):
    REST_URL = "http://%s:%d/tasks/delete/%d" % (HOST, PORT, task_id)
    request = requests.get(REST_URL)
    if request.status_code == 200:
        #json_decoder = json.JSONDecoder()
        #status = json_decoder.decode(request.text)["status"]
        return True
    else:
        return False

def report(task_id):
    REST_URL = "http://%s:%d/tasks/report/%d" % (HOST, PORT, task_id)
    request = requests.get(REST_URL)
    if request.status_code == 200:
        json_decoder = json.JSONDecoder()
        r = json_decoder.decode(request.text)
        return r

def get_url_hosts_from_sock_apis(sigs):
    #if 'signatures' not in doc:
    #    return []
    #sigs = doc['signatures']

    urls = set()
    query_hosts = set()

    for sig in sigs:
        if sig['description'] == "Socket APIs were called.":
            for call in sig['data']:
                api_name = call['signs'][0]['value']['api']
                if api_name == 'send':
                    args = call['signs'][0]['value']['arguments']
                    sent_buffer = args[0]['value'] # may be HTTP header.
                    if len(sent_buffer) > 4:
                        sent_buffer += '\r\n'
                        #print sent_buffer

                        header = sent_buffer
                        h_dict = dict(re.findall(r"(?P<name>.*?): (?P<value>.*?)\r\n", header))
                        path = header.split('\n')[0].split(' ')[1]

                        url = "http://%s%s" % (h_dict['Host'], path)
                        urls.add(url)
        elif sig['description'] == "Network APIs were called.":
            for call in sig['data']:
                api_name = call['signs'][0]['value']['api']
                args = call['signs'][0]['value']['arguments']
                #args_string = ', '.join(["%s=%s" % (arg['name'], arg['value']) for arg in args])
                #api_string = "%s(%s)" % (api_name, args_string)
                #api_strs.append(api_string)

                if api_name == "getaddrinfo":
                    addr = args[1]['value']
                    query_hosts.add(addr)
                if api_name == "URLDownloadToFileW":
                    url = args[0]['value']
                    #loc = args[1]['value']
                    #url_dl.add(url+','+loc)
                    urls.add(url)
                if api_name == "InternetOpenUrlA":
                    url = args[0]['value']
                    urls.add(url)
    #return list(urls), list(query_hosts)
    return str(list(urls) + list(query_hosts))

def view_signatures(task_id):
    REST_URL = "http://%s:%d/tasks/view_signatures/%d" % (HOST, PORT, task_id)
    request = requests.get(REST_URL)
    if request.status_code == 200:
        json_decoder = json.JSONDecoder()
        if request.text:
            status = json_decoder.decode(request.text)
            return status

def reschedule_task(task_id):
    REST_URL = "http://%s:%d/tasks/reschedule/%d" % (HOST, PORT, task_id)
    request = requests.get(REST_URL)
    if request.status_code == 200:
        json_decoder = json.JSONDecoder()
        if request.text:
            status = json_decoder.decode(request.text)
            return status['new_task_id']

def query_tasks(task_ids):
    ret = []
    start_time = None
    for task_id in task_ids:
        sigs = None
        while sigs == None:
            status = view(task_id)
            if status == "reported":
                sigs = view_signatures(task_id)
                sig_pattern = get_url_hosts_from_sock_apis(sigs)
                start_time = None
                #delete_task(task_id)
            elif status == "running":
                if start_time == None:
                    start_time = int(time.time())
                else:
                    cur_time = int(time.time())
                    print start_time, cur_time, TIMEOUT
                    if cur_time - start_time > TIMEOUT:
                        old_task_id = task_id
                        task_id = reschedule_task(old_task_id)
                        delete_task(old_task_id)
                        logger.error("Reschedule the task %d to %d." % (old_task_id, task_id))
                        start_time = None
                    else:
                        logger.debug("Waiting for task %d [%s]." % (task_id, status))
                        time.sleep(3)
            else:
                logger.debug("Waiting for task %d [%s]." % (task_id, status))
                time.sleep(3)
        ret.append(sig_pattern)
    return ret

def cuckoo(file_paths):
    logger.info("Submit %d files to cuckoo." % len(file_paths))
    task_ids = submit_files(file_paths)
    logger.info("Waiting for %d results from cuckoo." % len(file_paths))
    logger.info("Task id: %s" % (task_ids))
    query_results = query_tasks(task_ids)
    logger.info("Finished.")
    return query_results

if __name__ == "__main__":
    #SAMPLE_FILE = "/home/xuweilin/coder/sandbox/cuckoo/requirements.txt"
    #fpath = "../results/classifier=hidost,popsz=100,maxgen=3,mutprob=0.2,extnum=3,stopfit=0.00,start=F3B9663A01A73C5ECA9D6B2A0519049E.pdf/variants/generation_3/variant_98.pdf"
    fpath = sys.argv[1]
    fname = fpath.split('=')[-1].replace('/', '_')
    task_id = submit(fpath, fname)
    print view(task_id)


