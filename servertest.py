from fabric.api import *
from fabric.network import *
from utils import insert_log

@parallel
@roles('server')
def gfs_check():
    """
    Check gfs state on server. If there is no response, send alert that gfs is down.
    """
    with settings( hide('warnings', 'running', 'stdout', 'stderr'), warn_only=True):
        fs = run('ls /drupal/files/file.png')

    if not fs:
        msg = "Subject: GFS down!! \n"
        s = smtplib.SMTP('localhost')
        s.sendmail('fabricapi', conf.to_diwanee, msg)
        s.quit()
        insert_log("GFS down!!")

@roles('server')
def sql_process():
    """
    Check if there are more than certain number of active sql processes and send alert if true.
    """
    with settings( hide('warnings', 'running', 'stdout', 'stderr'), warn_only=True):
        sql_state = run(' mysql -e "show processlist"| grep -i query |wc -l')
        if sql_state > 45:
            processlist = run('mysql -e "show full processlist\G"')
            insert_log("SQL process list on lower high value")


@parallel
@roles('live')
def meminfo():
    """
    Check memory info on all servers and send mail alert if below treshold.
    """
    with settings( hide('warnings', 'running', 'stdout', 'stderr'), warn_only=True):
        memfree = run("free -m |grep cache: |awk '{print $4}'")
        memtotal = run("free -m |grep Mem: |awk '{print $2}'")
        load = run("uptime | awk -F'load average:' '{ print $2 }'")

    memory_percent = (float(memfree)/float(memtotal))*100

    if env.host == '127.0.0.1':
        if int(memory_percent) <= 5:
            msg = "Subject: LOW MEM on " + env.host + "\n"
            msg += "\n"

            # get process status
            f = run('ps aux | sort -nk +4 | tail |column -tx')
            msg += "\n\nProcesses by memory usage:\n\n"
            msg += f
            msg += "\n\n Memory percent:  " + memory_percent
            msg += "\n\n Server load:  " + load
            msg += "\n\n"

            insert_log("Left "+memfree+" free memory on host " + env.host)

            s = smtplib.SMTP('localhost')
            s.sendmail('fabric', conf.to_diwanee, msg)
            s.quit()

    else:
        if int(memory_percent) <= 15:
            msg = "Subject: LOW MEM on " + env.host + "\n"
            msg += "\n"

            # get process status
            f = run('ps aux | sort -nk +4 | tail |column -tx')
            msg += "\n\nProcesses by memory usage:\n\n"
            msg += f
            msg += "\n\n Memory percent:  " + memory_percent
            msg += "\n\n Server load:  " + load
            msg += "\n\n"

            insert_log("Left "+memfree+" free memory on host " + env.host)

            s = smtplib.SMTP('localhost')
            s.sendmail('fabric', conf.to_diwanee, msg)
            s.quit()

@parallel
@roles('server')
def swapinfo():
    """
    Check swap info on all servers and send mail alert if below treshold.
    """
    with settings( hide('warnings', 'running', 'stdout', 'stderr'), warn_only=True):
        swapfree = run("free -m |grep Swap: |awk '{print $4}'")
        swaptotal = run("free -m |grep Swap: |awk '{print $2}'")
        load = run("uptime | awk -F'load average:' '{ print $2 }'")

    swap_percent = (float(swapfree)/float(swaptotal))*100

    if int(swap_percent) <= 30:
        msg = "Subject: LOW SWAP on " + env.host + "\n"
        msg += "\n"

        # get process status
        f = run('''psres=$(ps -eo rss,vsz,user,pid,tty,time,cmd); set -- $(/bin/echo "$psres" | head -n1); shift; shift; echo "SWAP $*"; echo "$psres" | awk 'BEGIN {ORS=""; getline} {print $2 - $1 " "; for (i=3; i<NF; i++) print $i " "; print $NF "\n"}' | sort -rn | head |column -tx''' )
        msg += "\n\nProcesses by swap usage:\n\n"
        msg += f
        msg += "\n\n Swap Percent:  " + swap_percent
        msg += "\n\n Server load:  " + load
        msg += "\n\n"

        s = smtplib.SMTP('localhost')
        s.sendmail('fabric', conf.to_diwanee, msg)
        s.quit()
        insert_log("Left "+swapfree+" free swap space on " + env.host)
