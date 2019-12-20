# SPDX-License-Identifier: GPL-3.0-or-later
#
# (C) Copyright 2018-2019 CSI-Piemonte
# (C) Copyright 2019-2020 CSI-Piemonte

import psutil
from logging import getLogger
from time import gmtime, strftime
from datetime import datetime
from beecell.server.uwsgi_server.wrapper import uwsgi_util
from beecell.simple import truncate
import traceback


class UwsgiManagerError(Exception):
    pass


class UwsgiManager(object):
    """
    """
    def __init__(self):
        self.logger = getLogger(self.__class__.__module__+ u'.' + self.__class__.__name__)

    def _get_proc_infos(self, p, extended=False):
        """Internal function to get process infos
        
        :param p: process instance
        :return: dictionary with process infos
        """
        try:
            io_counters = p.io_counters()
            mem = p.memory_full_info()
            files = p.open_files()
            conns = p.connections(kind=u'all')
            
            res = {u'type': u'process',
                   u'pid': p.pid,
                   u'ppid': p.ppid(),
                   u'name': p.name(),
                   u'exe': p.exe(),
                   u'cmdline': p.cmdline(),
                   u'environ': p.environ(),
                   u'create_time': datetime.fromtimestamp(p.create_time()).strftime(u'%Y-%m-%d %H:%M:%S'),
                   u'status': p.status(),
                   u'state': p.is_running(),
                   u'cwd': p.cwd(),
                   u'user': {
                       u'name': p.username(),
                       u'uids': p.uids,
                       u'gids': p.gids},
                   u'stats': {
                       u'io': {
                           u'read': {
                               u'count': io_counters.read_count,
                               u'bytes': io_counters.read_bytes
                           },
                           u'write': {
                               u'count': io_counters.write_count,
                               u'bytes': io_counters.write_bytes
                           }
                       }
                   },
                   u'ctx_switches': p.num_ctx_switches(),
                   u'cpu': p.cpu_percent(interval=0.1),
                   u'mem': {
                       u'rss': mem.rss,
                       u'vms': mem.vms,
                       u'shared': mem.shared,
                       u'text': mem.text,
                       u'lib': mem.lib,
                       u'data': mem.data,
                       u'dirty': mem.dirty,
                       u'uss': mem.uss,
                       u'pss': mem.pss,
                       u'swap': mem.swap
                   },
                   u'fds': {
                       u'num': p.num_fds(),
                       u'files': [{
                           u'path': f.path,
                           u'fd': f.fd,
                           u'position': f.position,
                           u'mode': f.mode,
                           u'flags': f.flags
                       } for f in files]},
                   u'cpu': {
                       u'affinity': p.cpu_affinity()},
                   u'mem': {
                       u'use': p.memory_percent(memtype=u'rssu')},
                   u'conn': [{
                       u'fd': c.fd,
                       u'family': c.family,
                       u'laddr': c.laddr,
                       u'raddr': c.raddr,
                       u'status': c.status
                   } for c in conns],
                   u'threads': {u'num': p.num_threads(), u'list': p.threads()},
                   u'children': []}
            if extended is True:
                res[u'mem'][u'maps'] = p.memory_maps()
            
            self.logger.debug(u'Get process: %s' % p)
            for child in p.children(False):
                res[u'children'].append(self._get_proc_infos(child, extended=extended))
            return res
        except:
            self.logger.error(traceback.format_exc())
            raise UwsgiManagerError(u'Can not get process %s info' % p)
            
    def info(self, extended=False):
        """Get uwsgi instance infos

        memory:
            rss: aka "Resident Set Size", this is the non-swapped physical memory a process has used. On UNIX it
                 matches "top"'s RES column (see doc). On Windows this is an alias for wset field and it matches "
                 Mem Usage" column of taskmgr.exe.
            vms: aka "Virtual Memory Size", this is the total amount of virtual memory used by the process. On UNIX it
                 matches "top"'s VIRT column (see doc). On Windows this is an alias for pagefile field and it matches "
                 Mem Usage" "VM Size" column of taskmgr.exe.
            shared: (Linux) memory that could be potentially shared with other processes. This matches "top"'s SHR
                    column (see doc).
            text (Linux, BSD): aka TRS (text resident set) the amount of memory devoted to executable code. This
                               matches "top"'s CODE column (see doc).
            data (Linux, BSD): aka DRS (data resident set) the amount of physical memory devoted to other than
                               executable code. It matches "top"'s DATA column (see doc).
            lib (Linux): the memory used by shared libraries.
            dirty (Linux): the number of dirty pages.

        open files:
            path: the absolute file name.
            fd: the file descriptor number; on Windows this is always -1.
            position (Linux): the file (offset) position.
            mode (Linux): a string indicating how the file was opened, similarly open's mode argument. Possible values
                          are 'r', 'w', 'a', 'r+' and 'a+'. There's no distinction between files opened in bynary or
                          text mode ("b" or "t").
            flags (Linux): the flags which were passed to the underlying os.open C call when the file was opened (e.g.
                           os.O_RDONLY, os.O_TRUNC, etc).

        connections:
            fd: the socket file descriptor. This can be passed to socket.fromfd() to obtain a usable socket object.
                This is only available on UNIX; on Windows -1 is always returned.
            family: the address family, either AF_INET, AF_INET6 or AF_UNIX.
            type: the address type, either SOCK_STREAM or SOCK_DGRAM.
            laddr: the local address as a (ip, port) tuple or a path in case of AF_UNIX sockets.
            raddr: the remote address as a (ip, port) tuple or an absolute path in case of UNIX sockets. When the r
                   emote endpoint is not connected you'll get an empty tuple (AF_INET) or None (AF_UNIX). On Linux
                   AF_UNIX sockets will always have this set to None.
            status: represents the status of a TCP connection. The return value is one of the psutil.CONN_* constants.
                    For UDP and UNIX sockets this is always going to be psutil.CONN_NONE.
                        
        :param extended: if True print processes memory maps
        :raise UwsgiManagerError:
        """
        master_proc = psutil.Process(int(uwsgi_util.masterpid()))
        resp = self._get_proc_infos(master_proc, extended=extended)
        self.logger.debug(u'Get uwsgi processes: %s' % truncate(resp))
        return resp
    
    def stats(self):
        """Get uwsgi instance statistics
        
        :raise UwsgiManagerError:
        """
        try:
            timestamp = strftime(u'%d %b %Y %H:%M:%S +0000', gmtime())
            
            resp = {
                u'timestamp': timestamp,
                u'workers': uwsgi_util.workers(),
                u'masterpid': uwsgi_util.masterpid(),
                u'tot_requests': uwsgi_util.total_requests(),
                u'mem': uwsgi_util.mem()}
            self.logger.debug(u'Get uwsgi workers stats: %s' % truncate(resp))
            return resp
        except:
            raise UwsgiManagerError(u'Can not get info for uwsgi server')

    def reload(self):
        """Reload uwsgi instance
        
        :raise UwsgiManagerError:
        """
        try:
            pid = uwsgi_util.masterpid()
            timestamp = strftime(u'%d %b %Y %H:%M:%S +0000', gmtime())
            reloadState = uwsgi_util.reload()
            resp = {u'timestamp': timestamp, u'msg': str(reloadState)}
        
            self.logger.debug(u'Reload uwsgi instance %s: %s' % (pid, resp))
            return resp
        except:
            raise UwsgiManagerError(u'Can not reload uwsgi server')
