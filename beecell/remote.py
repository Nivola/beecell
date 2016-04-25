import socket
import os
import paramiko
from logging import getLogger
import httplib2
import httplib
import urllib2
import urllib3
import ujson as json
from time import time
import base64
import ssl
import re
from beecell.simple import truncate
from urllib3.util.ssl_ import create_urllib3_context

urllib3.disable_warnings()

class Urllib2MethodRequest(urllib2.Request):
    """
    from: http://stackoverflow.com/questions/21243834/doing-put-using-python-urllib2
    """
    def __init__(self, *args, **kwargs):
        if 'method' in kwargs:
            self._method = kwargs['method']
            del kwargs['method']
        else:
            self._method = None
        return urllib2.Request.__init__(self, *args, **kwargs)

    def get_method(self, *args, **kwargs):
        if self._method is not None:
            return self._method
        return urllib2.Request.get_method(self, *args, **kwargs)

class RemoteException(Exception):
    def __init__(self, value, code=0):
        self.value = value
        self.code = code
    
    def __str__(self):
        return "<RemoteException 'value':'%s', 'code':%s>" % (self.value, self.code)

class RemoteClient(object):
    def __init__(self, conn, user=None, pwd=None, proxy=None, keyfile=None,
                 certfile=None):
        """
        :param conn: Request connection. Ex. {'host':'10.102.90.30', 
                                              'port':80,
                                              'path':'/api',
                                              'proto':'http'} 
        :param proxy: proxy server. Ex. ('proxy.it', 3128) [default=None]
        """
        self.logger = getLogger(self.__class__.__module__+ \
                                '.'+self.__class__.__name__)        
        
        self.syspath = os.path.expanduser("~")
        self.conn = conn
        self.user = user
        self.pwd = pwd
        self.h = httplib2.Http(".cache")
        if user is not None:
            self.h.add_credentials(user, pwd)
        self.proxy = proxy
        
        self.keyfile = keyfile
        self.certfile = certfile

    def run_ssh_command(self, cmd, user, pwd, port=22):
        '''
        Run remote command using ssh connection
        Paramiko 1.8 doesn't work with ECDSA key hashing algorithm. Ubuntu 12+ use ECDSA as default.
        To set RSA open /etc/ssh/sshd_config and comment row 'HostKey /etc/ssh/ssh_host_ecdsa_key', then 
        restart ssh service
        '''
        '''
        import paramiko, base64
        key = paramiko.RSAKey(data=base64.decodestring('AAA...'))
        client = paramiko.SSHClient()
        client.get_host_keys().add('ssh.example.com', 'ssh-rsa', key)
        client.connect('ssh.example.com', username='strongbad', password='thecheat')
        stdin, stdout, stderr = client.exec_command('ls')
        for line in stdout:
            print '... ' + line.strip('\n')
        client.close()        
        '''
        try:
            client = paramiko.SSHClient()
            #key = paramiko.RSAKey(data=base64.decodestring('AAA...'))
            #client.load_host_keys(self.syspath + "/.ssh/known_hosts")
            client.set_missing_host_key_policy(paramiko.MissingHostKeyPolicy())
            #client.set_missing_host_key_policy(paramiko.WarningPolicy)
            #client.load_system_host_keys()
            
            client.connect(self.conn, 
                           port, 
                           username=user, 
                           password=pwd,
                           #timeout=None, 
                           #allow_agent=True, 
                           look_for_keys=False, 
                           compress=False)
            stdin, stdout, stderr = client.exec_command(cmd)
            res = {'stdout':[], 'stderr':stderr.read()}            
            for line in stdout:
                res['stdout'].append(line.strip('\n'))         
            '''if len(stderr.read()) != 0:
              print 'ERROR:'
              print stderr.read()
            print stdout.read()
            print stderr.read()'''

            client.close()
            return res
        except Exception as ex:
            raise RemoteException(ex) 

    def run_tcp_command(self, cmd, port):
        '''
        Run remote command using generic tcp socket connection
        '''
        try:
            response = []
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((self.conn, port))
            sock.sendall(cmd)
            response.append(sock.recv(1024))
            sock.close()
            return response
        except Exception as ex:
            raise RemoteException(ex)

    def run_http_request(self, proto, path, method, 
                               data='', headers={}, port=80, timeout=30):
        """
        :param proto: Request proto. Ex. http, https
        :param host: Request host. Ex. 10.102.90.30
        :param port: Request port. [default=80]
        :param path: Request path. Ex. /api/
        :param method: Request method. Ex. GET, POST, PUT, DELETE
        :param headers: Request headers. [default={}]. Ex. 
                        {"Content-type": "application/x-www-form-urlencoded",
                         "Accept": "text/plain"}
        :param data: Request data. [default={}]. Ex. 
                       {'@number': 12524, '@type': 'issue', '@action': 'show'}
        :param timeout: Request timeout. [default=30s]
        :raise RemoteException:
        """
        try:
            self.logger.debug('Send http %s request to %s://%s:%s%s' % 
                              (method, proto, self.conn, port, path))
            if proto == 'http':       
                conn = httplib.HTTPConnection(self.conn, port, timeout=timeout)
            else:
                conn = httplib.HTTPSConnection(self.conn, port, timeout=timeout)
            conn.request(method, path, data, headers)
            response = conn.getresponse()
            self.logger.debug('Response status: %s %s' % 
                              (response.status, response.reason))
            if response.status in [200, 400]:
                res = response.read()
                self.logger.debug(response.getheader('Content-type'))
                if response.getheader('Content-type') == 'application/json':
                    res_dict = json.loads(res)
                    #self.logger.debug('Response data: \n %s' % self.pp.pformat(res_dict))
                    return res_dict
                else:
                    #self.logger.debug('Response data: \n %s' % res)
                    return res
            conn.close()
            return None
        except Exception as ex:
            raise RemoteException(ex)    
        
    def run_http_request2(self, path, method, data='', headers={}, timeout=30):
        """Http client. Usage:
            res = http_client2('https', '/api', 'POST',
                                port=443, data='', headers={})        
        
        :param proto: Request proto. Ex. http, https
        :param host: Request host. Ex. 10.102.90.30
        :param port: Request port. [default=80]
        :param path: Request path. Ex. /api/
        :param method: Request method. Ex. GET, POST, PUT, DELETE
        :param headers: Request headers. [default={}]. Ex. 
                        {"Content-type": "application/x-www-form-urlencoded",
                         "Accept": "text/plain"}
        :param data: Request data. [default={}]. Ex. 
                       {'@number': 12524, '@type': 'issue', '@action': 'show'}
        :param timeout: Request timeout. [default=30s]
        :raise RemoteException:
        """
        start = time()
        path = self.conn['path'] + path
        proto = self.conn['proto']
        host = self.conn['host']
        if 'port' not in self.conn:
            if proto == 'http':
                port = 80
            else:
                port = 443
        else:
            port = self.conn['port']
        
        # set simple authentication
        auth = base64.encodestring('%s:%s' % (self.user, self.pwd)).replace('\n', '')
        headers["Authorization"] = "Basic %s" % auth
        
        self.logger.debug('Send http %s request to %s://%s:%s%s' % 
                          (method, proto, host, port, path))
        self.logger.debug('Send headers: %s' % headers)
        if data.lower().find('password') < 0:
            self.logger.debug('Send data: %s' % data)
        else:
            self.logger.debug('Send data: XXXXXXXXX')
        try:
            _host = host
            _port = port
            _headers = headers
            if self.proxy is not None:
                _host = self.proxy[0]
                _port = self.proxy[1]
                _headers = {}
                path = "%s://%s:%s%s" % (proto, host, port, path)
            
            if proto == 'http':       
                conn = httplib.HTTPConnection(_host, _port, timeout=timeout)
            else:
                '''
                # python >= 2.7.9
                if version_info > (2,7,8):
                    try:
                        ctx = ssl.create_default_context()
                        ctx.verify_mode = ssl.CERT_NONE
                        ctx.check_hostname = False
                        ctx = ssl._create_unverified_context()      
                    except:
                        pass
                # python < 2.7.9                        
                else:
                    try:
                        ssl._create_default_https_context = ssl._create_unverified_context
                    except:
                        pass

                ssl._create_default_https_context = ssl._create_unverified_context'''
                if self.keyfile is None:
                    try:
                        ssl._create_default_https_context = ssl._create_unverified_context
                    except:
                        pass
                    #ctx = create_urllib3_context(cert_reqs=ssl.CERT_NONE)
                    #ssl._create_default_https_context = ssl._create_unverified_context
                conn = httplib.HTTPSConnection(_host, _port, timeout=timeout,
                                               key_file=self.keyfile, 
                                               cert_file=self.certfile)
            if self.proxy is not None:
                conn.set_tunnel(host, port=port, headers=headers)
                self.logger.debug("set proxy %s" % self.proxy)
                headers = None
            
            conn.request(method, path, data, _headers)
            response = conn.getresponse()
            content_type = response.getheader('content-type')
            self.logger.debug('Response status: %s' % response.status)
            self.logger.debug('Response content-type: %s' % content_type)
            
        except httplib.HTTPException as ex:
            raise RemoteException(ex, 400)            

        # evaluate response status
        # BAD_REQUEST     400     HTTP/1.1, RFC 2616, Section 10.4.1
        if response.status == 400:
            res = response.read()
            self.logger.debug('Response data: %s' % truncate(res))
            raise RemoteException('BAD_REQUEST : %s' % res, 400)
  
        # UNAUTHORIZED           401     HTTP/1.1, RFC 2616, Section 10.4.2
        elif response.status == 401:
            res = response.read()
            self.logger.debug('Response data: %s' % truncate(res))            
            raise RemoteException('UNAUTHORIZED : %s' % res, 401)
        
        # PAYMENT_REQUIRED       402     HTTP/1.1, RFC 2616, Section 10.4.3
        
        # FORBIDDEN              403     HTTP/1.1, RFC 2616, Section 10.4.4
        elif response.status == 403:
            res = response.read()
            self.logger.debug('Response data: %s' % truncate(res))            
            raise RemoteException('FORBIDDEN : %s' % res, 403)
        
        # NOT_FOUND              404     HTTP/1.1, RFC 2616, Section 10.4.5
        elif response.status == 404:
            res = response.read()
            self.logger.debug('Response data: %s' % truncate(res))            
            raise RemoteException('NOT_FOUND : %s' % res, 404)        
        
        # METHOD_NOT_ALLOWED     405     HTTP/1.1, RFC 2616, Section 10.4.6
        elif response.status == 405:
            res = response.read()
            self.logger.debug('Response data: %s' % truncate(res))            
            raise RemoteException('METHOD_NOT_ALLOWED : %s' % res, 405)
        
        # NOT_ACCEPTABLE         406     HTTP/1.1, RFC 2616, Section 10.4.7
        elif response.status == 406:
            res = response.read()
            self.logger.debug('Response data: %s' % truncate(res))            
            raise RemoteException('NOT_ACCEPTABLE : %s' % res, 405)        
        
        # PROXY_AUTHENTICATION_REQUIRED     407     HTTP/1.1, RFC 2616, Section 10.4.8
        
        # REQUEST_TIMEOUT        408
        elif response.status == 408:         
            raise RemoteException('REQUEST_TIMEOUT', 408)
        
        # CONFLICT               409
        elif response.status == 409:
            res = response.read()
            self.logger.debug('Response data: %s' % truncate(res))            
            raise RemoteException('CONFLICT : %s' % res, 409)
        
        # UNSUPPORTED_MEDIA_TYPE 415
        elif response.status == 415:
            res = response.read()
            self.logger.debug('Response data: %s' % truncate(res))            
            raise RemoteException('UNSUPPORTED_MEDIA_TYPE : %s' % res, 415)    
        
        # INTERNAL SERVER ERROR  500
        elif response.status == 500:
            raise RemoteException('CLOUDAPI_SERVER_ERROR', 500)        
        
        # NO_CONTENT             204    HTTP/1.1, RFC 2616, Section 10.2.5            
        elif response.status == 204:
            res = None
            conn.close()
            return res
        
        # OK                     200    HTTP/1.1, RFC 2616, Section 10.2.1
        # CREATED                201    HTTP/1.1, RFC 2616, Section 10.2.2
        # ACCEPTED               202    HTTP/1.1, RFC 2616, Section 10.2.3
        # NON_AUTHORITATIVE_INFORMATION    203    HTTP/1.1, RFC 2616, Section 10.2.4
        # RESET_CONTENT          205    HTTP/1.1, RFC 2616, Section 10.2.6
        # PARTIAL_CONTENT        206    HTTP/1.1, RFC 2616, Section 10.2.7
        # MULTI_STATUS           207    WEBDAV RFC 2518, Section 10.2
        elif re.match('20[0-9]+', str(response.status)):
            res = response.read()
            self.logger.debug('Response data: %s' % truncate(res))
            if content_type == 'application/json':
                res_dict = json.loads(res)
                conn.close()
                return res_dict
            else:
                conn.close()
                return res
        
        return None
    
    def run_http_request3(self, path, method, data='', headers={}, timeout=30):
        """Http client. Usage:
            res = http_client2('https', 'host1', '/api', 'POST',
                                port=443, data='', headers={})        
        
        :param proto: Request proto. Ex. http, https
        :param host: Request host. Ex. 10.102.90.30
        :param port: Request port. [default=80]
        :param path: Request path. Ex. /api/
        :param method: Request method. Ex. GET, POST, PUT, DELETE
        :param headers: Request headers. [default={}]. Ex. 
                        {"Content-type": "application/x-www-form-urlencoded",
                         "Accept": "text/plain"}
        :param data: Request data. [default={}]. Ex. 
                       {'@number': 12524, '@type': 'issue', '@action': 'show'}
        :param timeout: Request timeout. [default=30s]
        :raise RemoteException:
        """
        start = time()
        path = self.conn['path'] + path
        proto = self.conn['proto']
        host = self.conn['host']
        if 'port' not in self.conn:
            if proto == 'http':
                port = 80
            else:
                port = 443
        else:
            port = self.conn['port']
        
        # set simple autheniticatin
        auth = base64.encodestring('%s:%s' % (self.user, self.pwd)).replace('\n', '')
        headers["Authorization"] = "Basic %s" % auth
        
        self.logger.debug('Send http %s request to %s://%s:%s%s' % 
                          (method, proto, host, port, path))
        self.logger.debug('Send headers: %s' % headers)
        if data.lower().find('password') < 0:
            self.logger.debug('Send data: %s' % data)
        else:
            self.logger.debug('Send data: XXXXXXXXX')
        try:
            url = "%s://%s:%s%s" % (proto, host, port, path)
                        
            if self.proxy is None: 
                conn = urllib3.PoolManager(timeout=timeout)
            else:
                conn = urllib3.ProxyManager(self.proxy, timeout=timeout)
            response = conn.urlopen(method, url, body=data, headers=headers)
        except Exception as ex:
            raise RemoteException(ex, 400)            

        # evaluate response status
        # BAD_REQUEST     400     HTTP/1.1, RFC 2616, Section 10.4.1
        if response.status == 400:
            raise RemoteException('BAD_REQUEST', 400)
  
        # UNAUTHORIZED           401     HTTP/1.1, RFC 2616, Section 10.4.2
        elif response.status == 401:
            raise RemoteException('UNAUTHORIZED', 401)
        
        # PAYMENT_REQUIRED       402     HTTP/1.1, RFC 2616, Section 10.4.3
        
        # FORBIDDEN              403     HTTP/1.1, RFC 2616, Section 10.4.4
        elif response.status == 403:
            raise RemoteException('FORBIDDEN', 403)
        
        # NOT_FOUND              404     HTTP/1.1, RFC 2616, Section 10.4.5
        
        # METHOD_NOT_ALLOWED     405     HTTP/1.1, RFC 2616, Section 10.4.6
        elif response.status == 405:
            raise RemoteException('METHOD_NOT_ALLOWED', 405)
        # NOT_ACCEPTABLE         406     HTTP/1.1, RFC 2616, Section 10.4.7
        
        # PROXY_AUTHENTICATION_REQUIRED     407     HTTP/1.1, RFC 2616, Section 10.4.8
        
        # REQUEST_TIMEOUT        408
        elif response.status == 408:
            raise RemoteException('REQUEST_TIMEOUT', 408)
        
        # INTERNAL SERVER ERROR  500
        elif response.status == 500:
            raise RemoteException('CLOUDAPI_SERVER_ERROR', 500)        
        
        # OK                     200     HTTP/1.1, RFC 2616, Section 10.2.1
        elif response.status == 200:
            res = response.data
            self.logger.debug('Response data: %s' % truncate(res))
            if headers['Accept'] == 'json':
                res_dict = json.loads(res)
                #conn.close()
                return res_dict
            else:
                #conn.close()
                return res
        return None            
        
class RemoteManager(object):
    '''
    Method to install some software on a remote portal2.
    '''
    def __init__(self, host):
        '''
        host : istance of class Host
        '''        
        self.syspath = os.path.expanduser("~")
        self.conn = host
        self.remoteClient = RemoteClient(self.conn.name)
    
    def detect_distribution(self):
        '''
        '''
        # check Linux distrbution
        cmd = "lsb_release -a"
        res = self.remoteClient.run_ssh_command(cmd, 
                                                self.conn.ssh2['user'], 
                                                self.conn.ssh2['pwd'])
    
        if len(res['stdout']) > 0:
            res = {'distributor_id':res['stdout'][0].split(':\t')[1],
                   'description':res['stdout'][1].split(':\t')[1],
                   'Release':res['stdout'][2].split(':\t')[1],
                   'codename':res['stdout'][3].split(':\t')[1],}
            return res
        else:
            return None

    def detect_python(self):
        cmd = "which python"
        res = self.remoteClient.run_ssh_command(cmd, 
                                                self.conn.ssh2['user'], 
                                                self.conn.ssh2['pwd'])
        if len(res['stdout']) > 0:
            cmd = "python -V"
            res = self.remoteClient.run_ssh_command(cmd, 
                                                    self.conn.ssh2['user'], 
                                                    self.conn.ssh2['pwd'])
            return res['stderr'].rstrip().lstrip('Python ')
        else:
            return None

    def detect_gcc(self):
        cmd = "which gcc"
        res = self.remoteClient.run_ssh_command(cmd, 
                                                self.conn.ssh2['user'], 
                                                self.conn.ssh2['pwd'])
        if len(res['stdout']) > 0:
            cmd = "gcc --version"
            res = self.remoteClient.run_ssh_command(cmd, 
                                                    self.conn.ssh2['user'], 
                                                    self.conn.ssh2['pwd'])
            return res['stdout'][0]
        else:
            return None

    def detect_uwsgi(self):
        cmd = "which uwsgi"
        res = self.remoteClient.run_ssh_command(cmd, 
                                                self.conn.ssh2['user'], 
                                                self.conn.ssh2['pwd'])
        if len(res['stdout']) > 0:
            cmd = "uwsgi --version"
            res = self.remoteClient.run_ssh_command(cmd, 
                                                    self.conn.ssh2['user'], 
                                                    self.conn.ssh2['pwd'])
            return res['stdout'][0]
        else:
            return None

    def install_uwsgi(self, version):
        '''
        exec as root
        $ apt-get install -qq python-setuptools
        $ pip install -U uwsgi
        '''
        ress = []
        currentVersion = self.detect_uwsgi()
        if (currentVersion == None or currentVersion < version):
            cmds = ['apt-get install -qq python-setuptools',
                    'pip install -U uwsgi']
            for cmd in cmds:
                res = self.remoteClient.run_ssh_command(cmd, 
                                                        self.conn.ssh2['user'], 
                                                        self.conn.ssh2['pwd'])
                ress.append(res)
            return ress
        else:
            return None
        
    def uninstall_uwsgi(self):
        '''
        exec as root
        $ pip uninstall uwsgi
        '''
        ress = []
        currentVersion = self.detect_uwsgi()
        if (currentVersion != None):
            cmds = ['pip uninstall -y uwsgi',
                    'rm -rf `which uwsgi`']
            for cmd in cmds:
                res = self.remoteClient.run_ssh_command(cmd, 
                                                        self.conn.ssh2['user'], 
                                                        self.conn.ssh2['pwd'])
                ress.append(res)
            return ress
        else:
            return None
          
    def create_directory(self, directory):
        '''
        '''     
        cmd = "ls %s" % directory
        res = self.remoteClient.run_ssh_command(cmd, 
                                                self.conn.ssh2['user'], 
                                                self.conn.ssh2['pwd'])
        if len(res['stderr']):
            # directory doesn't exist
            cmd = "mkdir -p %s" % directory
            res = self.remoteClient.run_ssh_command(cmd, 
                                                    self.conn.ssh2['user'], 
                                                    self.conn.ssh2['pwd'])
            return 'created'
        else:
            return 'exists'