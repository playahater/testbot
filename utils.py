import logging, logging.handlers, sys, sqlite3
from configobj import ConfigObj

'''
db schema:
logs:   key, value
apis:   name, url, failed, datetime
webs:  name, url, ipaddress, failed, datetime

usage:
query = 'SELECT * FROM apis WHERE name="%s" AND time="%s"' %(name, time)
doquery(query)
'''
def dbquery(query):
    #file based db
    #conn = sqlite3.connect('database.db')

    #ram based db
    conn = sqlite3.connect(':memory:')

    c = conn.cursor()
    try:
        c.execute(query)
        conn.commit()
        yield c
    finally:
        c.close()

def parse_config(hosts=False, apis=False, mails=False):
    config = ConfigObj('conf.cfg')

    if hosts:
        webhosts = config['webhosts']
        enabled = []
        for host in webhosts.keys():
            if webhosts[host]['enabled'] == 'True':
                enabled.append(webhosts[host])
        return enabled

    if apis:
        apis = config['apis']
        enabled = []
        for api in apis.keys():
            if apis[api]['enabled'] == 'True':
                enabled.append(apis[api])
        return enabled

    if mails:
        mails = config['mails']
        enabled = []
        for mail in mails.keys():
                enabled.append(mails[mail])
        return enabled

def init_log():
    #boot up syslog configuraton
    sys_logger = logging.getLogger('fabric')
    sys_logger.setLevel(logging.INFO)
    handler = logging.handlers.SysLogHandler(address='/dev/log')
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    sys_logger.addHandler(handler)
    return sys_logger


def insert_log(sys_logger, message):
    sys_logger.warning(message)


#def insert_log_web(message):
    #sys_logger = logging.getLogger('webtest')
    #sys_logger.setLevel(logging.INFO)
    #handler = logging.handlers.SysLogHandler(address='/dev/log')
    #formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    #handler.setFormatter(formatter)
    #sys_logger.addHandler(handler)
    #sys_logger.info(message)

#class DictToObject:
    #"""
    #Create host object from dictionary.
    #"""
    #def __init__(self, dictionary):
        #for k, v in dictionary.items():
            #setattr(self, k, v)
