# SPDX-License-Identifier: GPL-3.0-or-later
#
# (C) Copyright 2018-2019 CSI-Piemonte

"""
Re-add sslwrap to Python 2.7.9
https://github.com/gevent/gevent/issues/477
"""

from ssl import PROTOCOL_SSLv23, CERT_NONE, CERT_REQUIRED, CERT_OPTIONAL
from warnings import warn
from sys import version_info

if version_info.major == 2 and version_info.minor == 7 and version_info.micro >= 8:
    from gevent import _sslgte279 as _source
else:
    import gevent._ssl2 as __ssl__
    import httplib
    
    OldSSLSocket = __ssl__.SSLSocket
    Oldwrap_socket = __ssl__.wrap_socket
    OldHTTPSConnection = httplib.HTTPSConnection
    
    class NewSSLSocket(OldSSLSocket):
        """Fix SSLSocket constructor in gevent socket.
        """
        def __init__(self, sock, keyfile=None, certfile=None, server_side=False, cert_reqs=CERT_NONE,
                     ssl_version=PROTOCOL_SSLv23, ca_certs=None, do_handshake_on_connect=True,
                     suppress_ragged_eofs=True, ciphers=None, server_hostname=None, _context=None):
            OldSSLSocket.__init__(self, sock, keyfile=keyfile, certfile=certfile, server_side=server_side,
                                  cert_reqs=cert_reqs, ssl_version=PROTOCOL_SSLv23, ca_certs=ca_certs,
                                  do_handshake_on_connect=do_handshake_on_connect,
                                  suppress_ragged_eofs=suppress_ragged_eofs, ciphers=ciphers)

    def new_wrap_socket(sock, keyfile=None, certfile=None, server_side=False, cert_reqs=CERT_NONE,
                        ssl_version=PROTOCOL_SSLv23, ca_certs=None, do_handshake_on_connect=True,
                        suppress_ragged_eofs=True, ciphers=None, server_hostname=None):
        return OldSSLSocket(sock, keyfile=keyfile, certfile=certfile, server_side=server_side, cert_reqs=cert_reqs,
                            ssl_version=ssl_version, ca_certs=ca_certs, do_handshake_on_connect=do_handshake_on_connect,
                            suppress_ragged_eofs=suppress_ragged_eofs, ciphers=ciphers)
    
    class NewHTTPSConnection(OldHTTPSConnection):
        def __init__(self, host, port=None, key_file=None, cert_file=None, strict=None, timeout=None,
                     source_address=None, context=None):
            OldHTTPSConnection.__init__(self, host, port=port, key_file=key_file, cert_file=cert_file, strict=strict,
                                        timeout=timeout, source_address=source_address)

    __ssl__.SSLSocket = NewSSLSocket
    __ssl__.wrap_socket = new_wrap_socket
    httplib.HTTPSConnection = NewHTTPSConnection
    
    warn('python <2.7.9 SSLSocket and wrap_socket patch loaded')
