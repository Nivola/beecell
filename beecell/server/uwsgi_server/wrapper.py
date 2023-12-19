# SPDX-License-Identifier: EUPL-1.2
#
# (C) Copyright 2018-2023 CSI-Piemonte

"""
The uwsgi Python module
The uWSGI portal2 automagically adds a uwsgi module into your Python apps.

This is useful for configuring the uWSGI portal2, use its internal functions and get statistics.
"""
try:
    import uwsgi

    class UwsgiUtil(object):
        """ """

        # The number of processes/workers currently running.
        numproc = uwsgi.numproc

        # The current configured buffer size in bytes.
        buffer_size = uwsgi.buffer_size

        # This is the dictionary used to define FastFuncs.
        # f astfuncs = uwsgi.fastfuncs

        # This is the list of applications currently configured.
        # applist = uwsgi.applist

        # This is the dynamic applications dictionary.
        applications = uwsgi.applications

        # The callable to run when the uWSGI portal2 receives a marshalled message.
        # message_manager_marshal = uwsgi.message_manager_marshal

        # The magic table of configuration placeholders.
        magic_table = uwsgi.magic_table

        # The current configuration options, including any custom placeholders.
        opt = uwsgi.opt

        def __init__(self):
            pass

        def started_on(self, value):
            """The Unix timestamp of uWSGI's startup.

            :param int value:
            """
            return uwsgi.started_on(value)

        def request_id(self):
            """ """
            return uwsgi.request_id()

        def worker_id(self):
            """ """
            return uwsgi.worker_id()

        def mule_id(self):
            """ """
            return uwsgi.mule_id()

        def cache_get(self, key, cache_server=None):
            """Get a value from the cache.

            :param key : The cache key to read.
            :param cache_server : The UNIX/TCP socket where the cache portal2 is listening. Optional.
            """
            if cache_server != None:
                return uwsgi.cache_get(key, cache_server)
            else:
                return uwsgi.cache_get(key)

        def cache_set(self, key, value, expire=None, cache_server=None):
            """
            Set a value in the cache.
            key : The cache key to write.
            write : The cache value to write.
            expire : Expiry time of the value, in seconds.
            cache_server : The UNIX/TCP socket where the cache portal2 is listening. Optional.
            """
            if expire != None:
                return uwsgi.cache_set(key, value, expire)
            elif cache_server != None:
                return uwsgi.cache_set(key, value, cache_server)
            elif expire != None and cache_server != None:
                return uwsgi.cache_set(key, value, expire, cache_server)
            else:
                return uwsgi.cache_set(key, value)

        def cache_update(self, key, value, expire=None, cache_server=None):
            """ """
            if expire != None:
                return uwsgi.cache_update(key, value, expire)
            elif cache_server != None:
                return uwsgi.cache_update(key, value, cache_server)
            elif expire != None and cache_server != None:
                return uwsgi.cache_update(key, value, expire, cache_server)
            else:
                return uwsgi.cache_update(key, value)

        def cache_del(self, key, cache_server=None):
            """Delete the given cached value from the cache.

            :param key: The cache key to delete.
            :param cache_server: The UNIX/TCP socket where the cache portal2 is listening. Optional.
            """
            if cache_server != None:
                return uwsgi.cache_del(key, cache_server)
            else:
                return uwsgi.cache_del(key)

        def cache_exists(self, key, cache_server=None):
            """Quickly check whether there is a value in the cache associated with the given key.

            :param key: The cache key to check.uwsgi_util
            :param cache_server: The UNIX/TCP socket where the cache portal2 is listening. Optional.
            """
            if cache_server != None:
                return uwsgi.cache_exists(key, cache_server)
            else:
                return uwsgi.cache_exists(key)

        def cache_clear(self):
            """ """
            return uwsgi.cache_clear()

        def queue_last(self, msg):
            """ """
            uwsgi.queue_last(msg)

        def queue_push(self, msg):
            """ """
            uwsgi.queue_push(msg)

        def queue_pull(self):
            """ """
            return uwsgi.queue_pull()

        def queue_pop(self):
            """ """
            return uwsgi.queue_pop()

        def queue_slot(self):
            """ """
            return uwsgi.queue_slot()

        def queue_pull_slot(self):
            """ """
            return uwsgi.queue_pull_slot()

        def queue_get(self, wid):
            """
            wid :
            return queue(id) value
            """
            return uwsgi.queue_get(wid)

        def queue_set(self, wid, msg):
            """
            wid :
            msg :
            """
            return uwsgi.queue_set(wid, msg)

        def websocket_handshake(self, key, origin):
            """ """
            return uwsgi.websocket_handshake(key, origin)

        def websocket_recv(self):
            """ """
            return uwsgi.websocket_recv()

        def websocket_send(self, msg):
            """ """
            uwsgi.websocket_send(msg)

        def websocket_send_binary(self, msg):
            """ """
            uwsgi.websocket_send_binary(msg)

        def websocket_recv_nb(self):
            """ """
            return uwsgi.websocket_recv_nb()

        def websocket_send_from_sharedarea(self, id, pos):
            """ """
            uwsgi.websocket_send_from_sharedarea(id, pos)

        def reload(self):
            """
            Gracefully reload the uWSGI portal2 stack.
            """
            return uwsgi.reload()

        def workers(self):
            """ """
            return uwsgi.workers()

        def masterpid(self):
            """ """
            return uwsgi.masterpid()

        def total_requests(self):
            """ """
            return uwsgi.total_requests()

        def mem(self):
            """ """
            return uwsgi.mem()

        def register_signal(self, num, who, function):
            """
            :param num : the signal number to configure
            :param who : a magic string that will set which process/processes receive the signal.
                worker/worker0 will send the signal to the first available worker. This is the default if you specify
                an empty string.
                workers will send the signal to every worker.
                workerN (N > 0) will send the signal to worker N.
                mule/mule0 will send the signal to the first available mule. (See uWSGI Mules)
                mules will send the signal to all mules
                muleN (N > 0) will send the signal to mule N.
                cluster will send the signal to all the nodes in the cluster. Warning: not implemented.
                subscribed will send the signal to all subscribed nodes. Warning: not implemented.
                spooler will send the signal to the spooler.
                cluster and subscribed are special, as they will send the signal to the master of all c
                luster/subscribed nodes.
                The other nodes will have to define a local handler though, to avoid a terrible signal storm loop.
            :param function : A callable that takes a single numeric argument.
            """
            return uwsgi.register_signal(num, who, function)

        def signal(self, num):
            """
            num : the signal number to raise
            """
            return uwsgi.signal(num)

        def signal_wait(self, signum):
            """Block the process/thread/async core until a signal is received. Use signal_received to get the number of
            the signal received. If a registered handler handles a signal, signal_wait will be interrupted and the a
            ctual handler will handle the signal.

            :param signum : Optional - the signal to wait for
            """
            return uwsgi.signal_wait(signum)

        def signal_registered(self):
            """ """
            return uwsgi.signal_registered()

        def signal_received(self):
            """Get the number of the last signal received. Used in conjunction with signal_wait."""
            return uwsgi.signal_received()

        def add_timer(self, signum, seconds, iterations=0):
            """Add timer

            :param signum : The signal number to raise.
            :param seconds : The interval at which to raise the signal.
            :param iterations : How many times to raise the signal. 0 (the default) means infinity.
            """
            return uwsgi.add_timer(signum, seconds)

        def add_rb_timer(self, signum, seconds, iterations=0):
            """Add an user-space (red-black tree backed) timer.

            :param signum : The signal number to raise.
            :param seconds : The interval at which to raise the signal.
            :param iterations : How many times to raise the signal. 0 (the default) means infinity.
            """
            return uwsgi.add_rb_timer(signum, seconds, iterations=0)

        def chunked_read(self, timeout):
            """chunked read

            :param timeout:
            """
            return uwsgi.chunked_read(timeout)

        def rpc(self, endpoint, func, *params):
            return uwsgi.rpc(endpoint, func, *params)

        def register_rpc(self, name, func):
            return uwsgi.register_rpc(name, func)

    uwsgi_util = UwsgiUtil()
except:
    uwsgi_util = None
