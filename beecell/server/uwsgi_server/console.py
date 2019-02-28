#!/usr/bin/env python

# SPDX-License-Identifier: GPL-3.0-or-later
#
# (C) Copyright 2018-2019 CSI-Piemonte

'''
Usage: console.py [options] [args...]
-s service -c command
  
Options:
  -h, --help               Print help and exit
  -v, --version            Print version and exit
  -c, --command=CMD        Command: start, stop, reload, trace
                           Require args = service name

Examples::

    start portal2: console.py -c start clsk_desk
    stop portal2: console.py -c stop clsk_desk
    kill portal2: console.py -c kill clsk_desk    
    reload portal2: console.py -c reload clsk_desk
'''
import subprocess
import getopt
import traceback
import sys
import psutil
from blessings import Terminal

VERSION = '0.1.0'

def run_command(command):
    p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    if p.returncode == 0:
        print out
        return 0
    else:
        print err
        return p.returncode

def main(run_path, argv):
    cmd = None
    p = None
    retcode = 0
    t = Terminal()
    
    try:
        opts, args = getopt.getopt(argv,"c:hv",["help", "cmd=",
                                                "version"])
    except getopt.GetoptError:
        print __doc__
        return 2
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print __doc__
            return 0
        elif opt in ("-v", "--version"):
            print "uwsgi console %s" % VERSION
            return 0        
        elif opt in ("-c", "--cmd"):
            cmd = arg
    
    cmd = args[0]
    
    # start single portal2
    bufsize = 1024
    if (cmd == "start"):
        # verify if service already running
        try:
            service = args[1]
            # read pid from file
            pid_file = file('%s/run/%s.pid' % (run_path, service))
            print t.yellow("Service %s is already running" % service)
            return 0             
        except:
            try:
                command = ['uwsgi', '--ini', '%s/etc/%s.ini' % (run_path, service)]
                print t.blue("Start uwsgi instance : %s" % service)
                retcode = run_command(command)
            except:
                traceback.print_exc(file=sys.stdout)
    elif (cmd == "stop"):
        try:
            service = args[1]
            command = ['uwsgi', '--stop', '%s/run/%s.pid' % (run_path, service)]
            print t.blue("Stop uwsgi portal2 : %s" % service)
            retcode = run_command(command)
        except:
            traceback.print_exc(file=sys.stdout)
    elif (cmd == "kill"):
        try:
            service = args[1]
            pid = None        
            for p in psutil.process_iter():
                if p.name == 'uwsgi' and p.cmdline == [service] and p.ppid == 1:
                    pid = p.pid
                    print(p.name, p.cmdline, p.pid, p.ppid)
            if pid is None:
                print t.yellow("Service %s is not running" % service)
                return 0

            command = ['kill', '-9', str(pid)]
            print t.red("Kill uwsgi instance : %s" % service)
            retcode = run_command(command)
        except:
            traceback.print_exc(file=sys.stdout)            
    elif (cmd == "reload"):
        try:
            service = args[1]
            command = ['uwsgi', '--reload', '%s/run/%s.pid' % (run_path, service)]
            print t.yellow("Reload uwsgi portal2 : %s" % service)
            retcode = run_command(command)
        except:
            traceback.print_exc(file=sys.stdout)
    elif (cmd == "status"):
        try:
            service = args[1]
            # read pid from file
            pid_file = file('%s/run/%s.pid' % (run_path, service))
        except:
            print t.red("Service %s is not running" % service)
            return 1
            
        try:
            pid = int(pid_file.read())
            pid_file.close()
            # read proc info
            if psutil.pid_exists(pid):
                p = psutil.Process(pid)
                pts = ','.join([str(td.id) for td in p.threads()])
                parent = p.parent
                ppid = p.ppid()
                pp = psutil.Process(ppid)
                print t.blue("Process tree:")
                print t.blue(" %-6s %-8s %-20s" % (ppid, pp.name, pp.exe))
                print t.blue(" |- %-6s %-8s %-20s [%s]" % (pid, p.name, p.exe, pts))
                
                for c in p.children(recursive=True):
                    pc = psutil.Process(c.pid)
                    pcts = ','.join([str(td.id) for td in pc.threads()])                               
                    print t.blue("    |- %-6s %-8s %-20s [%s]" % (c.pid, pc.name, pc.exe, pcts))
                        
                print t.blue("\nProcess info:")
                print t.blue(" path : %s" % p.cwd())
                print t.blue(" status : %s" % str(p.status))
                print t.blue(" permissions : %s, %s" % (p.uids, p.gids))
                print t.blue(" memory : %s" % str(p.memory_info_ex()))
                #sys.stdout.write(" memory map: %s\n" % str(p.get_memory_maps()))
                print t.blue(" open files :")
                for fd in p.open_files():
                    print t.blue(" |- fd:%s, file:%s" % (fd.fd, fd.path))
                print t.blue(" connections :")
                for c in p.connections():
                    print t.blue(" |- fd:%s, family:%s, type:%s, laddr:%s, raddr:%s, status:%s" % 
                                     (c.fd, c.family, c.type, c.laddr, 
                                      c.raddr, c.status))
                
            #command = ['uwsgi', '--reload', '%s/run/%s.pid' % (run_path, service)]
            #print "Reload uwsgi portal2 : %s" % service
            
            
            #retcode = run_command(command)
        except:
            traceback.print_exc(file=sys.stdout)       
    elif (cmd == "trace"):
        try:
            service = args[1]
            command = ['uwsgi', '--connect-and-read', '%s/run/%s.tbsocket.*' % 
                       (run_path, service)]
            retcode = run_command(command)
        except:
            traceback.print_exc(file=sys.stdout) 
    elif (cmd == "log-uwsgi"):
        try:
            service = args[1]
            from sh import tail
            # runs forever
            for line in tail("-f", '%s/log/%s-uwsgi.log' % (run_path, service), _iter=True):
                sys.stdout.write(line)
        except:
            traceback.print_exc(file=sys.stdout)
    elif (cmd == "log"):
        try:
            service = args[1]
            from sh import tail
            # runs forever
            for line in tail("-f", '%s/log/%s.log' % (run_path, service), _iter=True):
                sys.stdout.write(line)
        except:
            traceback.print_exc(file=sys.stdout)             
    elif (cmd == "createdb"):
        try:
            command = ['uwsgi', '--ini', '%s/etc/shell.ini' % (run_path)]
            #sys.stdout.write("Create db")
            retcode = run_command(command)
        except:
            traceback.print_exc(file=sys.stdout)
    
    return retcode