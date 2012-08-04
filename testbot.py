import sys, time
from apitest import apis_check
from webtest import web_monitor, fix
from utils import init_log
from servertest import *
from fabric.api import *
from fabric.network import *
#from daemon import DaemonContext
#from daemon.runner import make_pidlockfile, is_pidfile_stale

env.user = 'username'
env.key_filename = ['/path/to/your_key']
env.roledefs = {
    'live': ['127.0.0.3'],
    'server': ['127.0.0.1', '127.0.0.2',],
}

def main():
    """
    Execution
    """

    startTime = time.time()

    #pidfile = make_pidlockfile('/tmp/test-daemon.pid', 0)

    #if is_pidfile_stale(pidfile):
            #pidfile.break_lock()

    #if pidfile.is_locked():
            #print 'daemon is running with PID %s already' % pidfile.read_pid()
            #sys.exit(0)

    #with DaemonContext(pidfile=pidfile):

    #define counters
    fix.count = 0
    apis_check.count = 0

    #initialize syslog configuration
    sys_logger = init_log()

    #crawl web hosts and log/email failures if any
    web_monitor(sys_logger)

    #execute(gfs_check)
    #execute(meminfo)
    #execute(swapinfo)

    #crawl API hosts and log/email failires if any
    execute(apis_check, sys_logger)

    #disconnect from all servers
    disconnect_all()
    #time.sleep(1)

    endTime = time.time()
    elapsedTime = endTime - startTime

    print elapsedTime

if __name__ == '__main__':
    # First arg is script name, skip it
    main()
