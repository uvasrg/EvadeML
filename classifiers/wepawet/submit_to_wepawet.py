#!/usr/bin/env python

"""
This script allows one to submit resources (URLs and files) for analysis.
The submission consists of 2 steps: URL submission and result retrieval.
1. To request the processing of a resource, use the -s option with the URL 
   or filename to be checked:
   $ python submit_to_wepawet.py -s 'http://www.cs.ucsb.edu/'
   <?xml version="1.0" encoding="utf-8" ?>
   
   <response state="ok">
      <hash>d6aeabfce7d73b7262030333bea80c24</hash>
   </response>
   
   The returned 'hash' uniquely identifies the analysis request. In case of
   errors, say unresolvable domain, you'll get back an error message.
   
2. To query the status of a processing request, use the -q option with
   the hash returned from the previous submission:
   $ python submit_to_wepawet.py -q d6aeabfce7d73b7262030333bea80c24

   <?xml version="1.0" encoding="utf-8" ?>

   <response state="ok">
       <status>processed</status>
       <url><![CDATA[http://www.cs.ucsb.edu]]></url>
       <report_url><![CDATA[http://192.168.2.2/view.php?type=js&hash=a60d8d724f03053591be2ed13ed62164&t=1249552727]]></report_url>
       <result>benign</result>
   </response> 
   
   If the resource has not been processed yet, you'll get a response
   similar to:
   <response state="ok">
      <status>queued</status>
   </response>

Limitations:
- only HTML/JS resources can be analyzed (no flash)

Comments/problems/bugs to wepawet@cs.ucsb.edu.
"""

import cgi
import getopt
import httplib
import itertools
import mimetools
import mimetypes
import os
import sys
import urllib
import urllib2
import urlparse

SERVER = 'wepawet.iseclab.org'
SUBMIT_PATH = '/services/upload.php'
QUERY_PATH  = '/services/query.php'
DOMAIN_PATH  = '/services/domain.php'
URL_PATH  = '/services/url.php'
ADDTL_HDRS_SEP = '@llweb_hdrs_sep@'

def __init_socks(socks_host, socks_port):
    try:
        import socket
        import socks
    except:
        print >>sys.stderr, """To connect via a SOCKS proxy you need the socks module.
It can be downloaded from http://socksipy.sourceforge.net
"""
    
        sys.exit(2)
    socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, socks_host, socks_port)
    socket.socket = socks.socksocket

class __MultiPartForm(object):
    """Accumulate the data to be used when posting a form.
    Copied from D. Hellmann, http://broadcast.oreilly.com/2009/07/pymotw-urllib2.html"""

    def __init__(self):
        self.form_fields = []
        self.files = []
        self.boundary = mimetools.choose_boundary()
        return
    
    def get_content_type(self):
        return 'multipart/form-data; boundary=%s' % self.boundary
    
    
    def add_field(self, name, value):
        """Add a simple field to the form data."""
        self.form_fields.append((name, value))
        return
    
    
    def add_file(self, fieldname, filename, fileHandle, mimetype=None):
        """Add a file to be uploaded."""
        body = fileHandle.read()
        if mimetype is None:
            mimetype = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
        self.files.append((fieldname, filename, mimetype, body))
        return
    
    def __str__(self):
        """Return a string representing the form data, including attached files."""
        # Build a list of lists, each containing "lines" of the
        # request. Each part is separated by a boundary string.
        # Once the list is built, return a string where each
        # line is separated by '\r\n'.
        parts = []
        part_boundary = '--' + self.boundary
        
        # Add the form fields
        parts.extend(
            [ part_boundary,
              'Content-Disposition: form-data; name="%s"' % name,
              '',
              value,
            ]
            for name, value in self.form_fields
        )
        
        # Add the files to upload
        parts.extend(
            [ part_boundary,
              'Content-Disposition: file; name="%s"; filename="%s"' % \
                (field_name, filename),
              'Content-Type: %s' % content_type,
              '',
              body,
            ]
            for field_name, filename, content_type, body in self.files
        )
        
        # Flatten the list and add closing boundary marker,
        # then return CR+LF separated data
        flattened = list(itertools.chain(*parts))
        flattened.append('--' + self.boundary + '--')
        flattened.append('')
        return '\r\n'.join(flattened)


class __DoNotRedirectHandler(urllib2.HTTPRedirectHandler):
    def http_error_301(self, req, fp, code, msg, headers):
        return fp

    def http_error_302(self, req, fp, code, msg, headers):
        fp.url = urlparse.urljoin(req.get_full_url(), headers['Location'])
        return fp
        
def wepawet_submit_file(file, analysis_opts, user=None, passwd=None):
    form = __MultiPartForm()
    form.add_field('resource_type', 'js')
    if user:
        form.add_field('user', user)
    if passwd:
        form.add_field('passwd', passwd)
    if analysis_opts.referer:
        form.add_field('referer', analysis_opts.referer)
    if analysis_opts.proxy:
        form.add_field("proxy", analysis_opts.proxy)
    if len(analysis_opts.addtl_headers) > 0:
        form.add_field("addtl_headers", ADDTL_HDRS_SEP.join(analysis_opts.addtl_headers))
    form.add_file('file', os.path.basename(file), fileHandle=open(file))
    body = str(form)

    req = urllib2.Request('http://' + SERVER + SUBMIT_PATH)
    req.add_header('Content-type', form.get_content_type())
    req.add_header('Content-length', len(body))
    req.add_data(body)

    response = urllib2.urlopen(req)
    res = response.read()
    return res

def wepawet_submit(url, analysis_opts, user=None, passwd=None):
    p = {
        'resource_type': 'js',
        'url': url
    }
    if user:
        p['user'] = user
    if passwd:
        p['passwd'] = passwd
    if analysis_opts.referer:
        p['referer'] = analysis_opts.referer
    if analysis_opts.proxy:
        p["proxy"] = analysis_opts.proxy
    if len(analysis_opts.addtl_headers) > 0:
        p["addtl_headers"] = ADDTL_HDRS_SEP.join(analysis_opts.addtl_headers)

    params = urllib.urlencode(p)

    req = urllib2.Request('http://' + SERVER + SUBMIT_PATH, params)
    response = urllib2.urlopen(req)
    res = response.read()
    return res

def wepawet_query(task_id):
    params = urllib.urlencode({
        'resource_type': 'js',
        'hash': task_id
    })
    req = urllib2.Request('http://' + SERVER + QUERY_PATH + '?' + params)
    response = urllib2.urlopen(req)
    res = response.read()
    return res

def wepawet_domain(domain):
    p = {
        'resource_type': 'js',
        'domain': domain
    }
    params = urllib.urlencode(p)
    req = urllib2.Request('http://' + SERVER + DOMAIN_PATH + '?' + params)
    response = urllib2.urlopen(req)
    res = response.read()
    return res

def wepawet_url(url):
    p = {
        'resource_type': 'js',
        'url': url
    }
    params = urllib.urlencode(p)
    req = urllib2.Request('http://' + SERVER + URL_PATH + '?' + params)
    response = urllib2.urlopen(req)
    res = response.read()
    return res

def usage(cmd):
    print """Usage: cmd OPTIONS
   -C,--credentials USER:PASSWD    use the given credentials
   -d,--domain DOMAIN              query if DOMAIN has been analyzed
   -h,--help                       print this message and exit
   -H,--header                     additional browser's header 
   -p,--socks-proxy-host           proxy host
   -P,--socks-proxy-port           proxy port
   -q,--query TASK_ID              query the status of a request
   -r,--referer URL                use URL as the initial referer
   -s,--submit URL                 submit URL for analysis
   -S,--server SERVER              analysis server
   -u,--url URL                    query if URL has been analyzed
   -v,--verbose                    be verbose
   -x,--browser-proxy              browser's proxy
"""

class AnalysisOptions:
    addtl_headers = []
    proxy = None
    referer = None

def main(argv=sys.argv):
    global SERVER

    try:
        opts, args = getopt.getopt(argv[1:], 
            "C:d:hH:p:P:q:r:s:S:u:vx:",
            ["credentials=", "domain=", "help", "header=", 
             "proxy-host=", "proxy-port=", 
             "query=", "referer=", "submit=", "server=", "url=", 
             "verbose", "browser-proxy"])
    except getopt.GetoptError, e:
        print str(e)
        usage(argv[0])
        return 1
    
    action = None
    resource = None
    task_id = None
    verbose = False
    socks_proxy_host = socks_proxy_port = None
    user = passwd = None
    analysis_opts = AnalysisOptions()
    for o,a in opts:
        if o in ('-C', '--credentials'):
            try:
                user, passwd = a.split(":", 1)
            except ValueError:
                print >>sys.stderr, "Invalid credentials format (USER:PASSWD)"
                return 1
        elif o in ('-d', '--domain'):
            action = 'domain'
            resource = a
        elif o in ('-h', '--help'):
            usage(argv[0])
            return 0
        elif o in ('-H', '--header'):
            analysis_opts.addtl_headers.append(a)
        elif o in ('-p', '--proxy-host'):
            socks_proxy_host = a
        elif o in ('-P', '--proxy-port'):
            socks_proxy_port = int(a)
        elif o in ('-q', '--query'):
            action = 'query'
            task_id = a
        elif o in ('-r', '--referer'):
            analysis_opts.referer = a
        elif o in ('-s', '--submit'):
            action = 'submit'
            resource = a
        elif o in ('-S', '--server'):
            SERVER = a
        elif o in ('-u', '--url'):
            action = 'url'
            resource = a
        elif o in ('-v', '--verbose'):
            verbose = True
        elif o in ('-x', '--browser-proxy'):
            analysis_opts.proxy = a
    
    if action is None:
        usage(argv[0])
        return 1
    
    if resource is not None and task_id is not None:
        usage(argv[0])
        return 1
    
    if socks_proxy_port or socks_proxy_host:
        if not socks_proxy_port:
            socks_proxy_port = 8888
        if not socks_proxy_host:
            socks_host = "localhost"
        __init_socks(socks_proxy_host, socks_proxy_port)
    
    httplib.HTTPConnection.debuglevel = 1
    
    if action == 'submit':
        if os.path.exists(resource):
            #print resource, analysis_opts, user, passwd
            r = wepawet_submit_file(resource, analysis_opts, user, passwd)
        else:
            #pass
            r = wepawet_submit(resource, analysis_opts, user, passwd)
    elif action == 'query':
        r = wepawet_query(task_id)
    elif action == 'domain':
        r = wepawet_domain(resource)
    elif action == 'url':
        r = wepawet_url(resource)
    
    print r

if __name__ == "__main__":
    sys.exit(main())
