import time, urllib2, httplib, re, logging, socket
from fabric.api import *
from mails import *
from utils import parse_config, insert_log
from threading import Thread, enumerate

#patch to deal with defective http servers
def patch_http_response_read(func):
    def inner(*args):
        try:
            return func(*args)
        except httplib.IncompleteRead, e:
            return e.partial

    return inner

#patch httplib
httplib.HTTPResponse.read = patch_http_response_read(httplib.HTTPResponse.read)

class URLThread(Thread):
    def __init__(self,url):
        super(URLThread, self).__init__()
        self.url = url
        self.response = None

    def run(self):

        # set socket timeout | 
        # possible fix for transfer encoding finished 
        # before reaching the expected size
        timeout = 20
        socket.setdefaulttimeout(timeout)

        try:
            self.response = urllib2.urlopen(self.url)
        except urllib2.URLError:
            if hasattr(e, 'reason'):
                insert_log('We failed to reach a server. Reason: '+ e.reason)
            elif hasattr(e, 'code'):
                insert_log('The server couldn\'t fulfill the request.Error code: '+ e.code)
            pass

def web_monitor(sys_logger):
    #crawl through the list, into html of each web page and check if data and status code are OK
    failed = crawl_all()

    if failed:
        fix(failed, sys_logger)
    else:
        insert_log(sys_logger, "WEB Monitor returned status OK")

def multi_get(uris,timeout=20.0):
    UPDATE_INTERVAL = 0.01

    def alive_count(lst):
        alive = map(lambda x : 1 if x.isAlive() else 0, lst)
        return reduce(lambda a,b : a + b, alive)
    threads = [ URLThread(uri) for uri in uris ]
    for thread in threads:
        thread.start()
    while alive_count(threads) > 0 and timeout > 0.0:
        timeout = timeout - UPDATE_INTERVAL
        time.sleep(UPDATE_INTERVAL)
    return [ (x.url, x.response) for x in threads ]

def crawl_all():
    """
    Crawl urls asynchronously and return url and it's response.
    """
    sites = []
    failed = {}

    hosts = parse_config(hosts=True)
    for url in hosts:
        sites.append(url['url'])

    #do some multi crawl on them all
    requests = multi_get(sites,timeout=25.5)

    for url, data in requests:
        failed_data = []
        for host in hosts:
            if host['url'] == url:
                html = data.read()
                match = re.search(host['match'], html)
                if not match or data.code not in (200,302):
                    failed_data.append(host['name'])
                    failed_data.append(data.code)
                    failed_data.append(html)
                    failed[url] = failed_data

    return failed

def bookie(func):
    func.count += 1

def fix(failed, sys_logger):

    hostname = []
    htmlcode = []
    htmldata = []

    bookie(fix)

    failed_urls = ', '.join(failed.keys())
    insert_log(sys_logger, failed_urls +" - "+ str(fix.count))

    values = failed.values()
    for name, code, html in values:
        hostname.append(name)
        htmlcode.append(code)
        htmldata.append(html)

    if fix.count <= 2:
        hosts = []
        hostconf = parse_config(hosts=True)
        for host in hostconf:
            for url, code in failed.iteritems():
                if host['url'] == url:
                    hosts.append(host['ip'])

        #define hosts
        env.hosts = hosts

        if fix.count == 1:
            #execute(apache_restart)
            print env.hosts + "execute(apache_restart)"
            site_email(hostname, failed.keys(), htmldata, htmlcode, status=True)
        elif fix.count == 2:
            #execute(clear_cache)
            print env.hosts + "execute(clear_cache)"
            site_email(hostname, failed.keys(), htmldata, htmlcode, status=True, rerun=True)

        time.sleep(5*fix.count)
        web_monitor(sys_logger)

    elif fix.count > 2:
        site_email(hostname, failed.keys(), htmldata, htmlcode)


@roles('server')
def clear_cache():
    """
    Wipe all drupal cache tables without confirmation.
    """
    with settings( hide('warnings', 'running', 'stdout', 'stderr'), warn_only=True):
        run('drush -r /var/www/html cc all -y')

@parallel
@roles('server')
def apache_restart():
    """
    Restart the Apache2 server.
    """
    with settings( hide('warnings', 'running', 'stdout', 'stderr'), warn_only=True):
        run('/etc/init.d/httpd restart')
