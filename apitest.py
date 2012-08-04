import time, re
from fabric.api import *
from mails import *
from webtest import bookie
from utils import parse_config, insert_log, dbquery

class apitest:
    def __init__(self, title, url, match, status, enabled):
        self.api_title = title
        self.api_url = url
        self.api_match = match
        self.api_status = status
        self.api_enabled = enabled

    def check(self, sys_logger):
        if self.api_enabled == 'True':
            with settings(hide('warnings', 'running', 'stdout', 'stderr'), warn_only=True):
                #define host from where api curl request should be triggered
                env.hosts = ['127.0.0.1']
                if self.api_title.lower() == 'broadband':
                    #html = run('curl --connect-timeout 30 -m 60 -k -d "param1=value1&param2=value2" %s' % api_url)
                    #html = run('curl --connect-timeout 30 -m 60 -k -d %s %s' % (api_params, api_url))
                    html = run('curl --connect-timeout 30 -m 30 -k %s' % self.api_url)
                    headers = run('curl -I -k %s' % self.api_url)
                else:
                    #html = run('curl --connect-timeout 30 -m 60 -d "param1=value1&param2=value2" %s' % api_url)
                    html = run('curl --connect-timeout 30 -m 30 %s' % self.api_url)
                    headers = run('curl -I %s' % self.api_url)

                content_match = re.search(self.api_match, html)
                header_match = re.search(self.api_status, headers)

            if header_match == None:
                api_email(self.api_title, headers, html, 1)
                insert_log(sys_logger, "API test failed for %s - no header retreived" % self.api_title)
            elif content_match == None:
                api_email(self.api_title, headers, html)
                insert_log(sys_logger, "API test failed for %s - no content retreived" % self.api_title)


def apistore(apiname):
    apiname.check = True

@roles('web3')
def apis_check(sys_logger):
    """
    Check APIs.
    """
    #start counter
    bookie(apis_check)
    #get config values
    apis = parse_config(apis=True)
    for api in apis:
        ap = apitest(api['name'], api['url'], api['match'], api['status'], api['enabled'])
        ap.check(sys_logger)
