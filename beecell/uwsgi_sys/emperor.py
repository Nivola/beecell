from gibbonutil.remote import RemoteClient
from gibbonutil.remote import RemoteManager
from gibbonutil.remote import RemoteExcpetion
from gibbon.manager.db.dto.emperor import Emperor

class EmperorManagerExcpetion(Exception):
  def __init__(self, value):
    self.value = value

  def __str__(self):
    return repr(self.value)

class EmperorManager(object):
    '''
    Class used to manage remote emperor instance.
    start :  uwsgi --ini emperor.ini 
    stop :   uwsgi --stop run/emperor.pid 
    reload : uwsgi --reload run/emperor.pid 
    '''
    def __init__(self, emperor):
        emperor = Emperor()
        '''
        host : istance of class Host
        '''
        self.host = emperor.host
        self.name = emperor.name
        if 'pid' in emperor.directory:
            self.pidDir = emperor.directory['pid']
        else:    
            self.pidDir = '/tmp/uwsgi/run'
        if 'log' in emperor.directory:
            self.logDir = emperor.directory['log']
        else:    
            self.logDir = '/tmp/uwsgi/log'
        if 'vassal' in emperor.directory:
            self.vassalSearchPath = emperor.directory['vassal']
        else:    
            self.vassalSearchPath = '/tmp/uwsgi/vassals/'
        self.uwsgiPath = ''
        self.uwsgiExec = 'uwsgi'
        #self.db_conn_string = ''
        self.statsPort = 1717
        
        if 'stats' in emperor.ports:
            self.statsPort = int(emperor.ports['stats'])
        else:    
            self.statsPort = 1717
        
        self.remoteClient = RemoteClient(self.host.name)
        self.remoteManager = RemoteManager(self.host)
        
        self.check = None
    
    '''
    def set_db_conn_string(self, db_conn_string):
        self.db_conn_string = db_conn_string        
    '''

    def check_environment(self):
        '''
        Check if directories exists over remote portal2 and create them if they don't exists
        '''
        try:
            self.check = {}
            # check distribution
            self.check['distro'] = self.remoteManager.detect_distribution()
            
            # check python
            self.check['python'] = self.remoteManager.detect_python()
            
            # check gcc
            self.check['gcc'] = self.remoteManager.detect_gcc()
            
            # check uwsgi
            self.check['uwsgi'] = self.remoteManager.detect_uwsgi()
            
            # check if self.pidDir exists
            self.check['pid_dir'] = self.remoteManager.create_directory(self.pidDir)
                
            # check if self.logDir exists
            self.check['log_dir'] = self.remoteManager.create_directory(self.logDir)
                
            # check if self.vassalSearchPath exists
            self.check['vassalSearchPath'] = self.remoteManager.create_directory(
                self.vassalSearchPath)
                
            return self.check
        except RemoteExcpetion as ex:
            raise EmperorManagerExcpetion('Error running check environment: '+str(ex))

    def start(self):
        '''
        Start emperor istance on a remote portal2
        uwsgi --ini emperor.ini
        #socket = :3031
        plugin = emperor_pg 
        emperor = pg://host=127.0.0.1 user=gibbon password=gibbon dbname=gibbon;SELECT name,config,ts FROM emperor_vassals
        # enable the master process 
        master = true
        #processes = 4
        #enable-threads
        #threads = 40
        procname = emperor
        daemonize = log/uwsgi-emperor.log
        pidfile = run/emperor.pid
        log-master
        vacuum = true
        #stats = 1717        
        '''
        if self.check == None:
            self.check_environment()
            
        if self.check['uwsgi'] == None:
            raise EmperorManagerExcpetion('uwsgi is not installed')
        
        try:
            params = [#'--plugin', 'emperor_pg',
                      #'--emperor', '"'+self.db_conn_string+'"',
                      '--emperor', '"'+self.vassalSearchPath+'*.ini"',
                      '--master',
                      '--procname', self.name,
                      '--daemonize', self.logDir+'/'+self.name+'.log',
                      '--pidfile', self.pidDir+'/'+self.name+'.pid',
                      '--log-master', '',
                      '--vacuum', 
                      '--stats', ":%s" % self.statsPort,
                      ]
            cmd = 'cd %s && %s %s' % (self.uwsgiPath,
                                      self.uwsgiExec, 
                                      ' '.join(params))
            res = self.remoteClient.run_ssh_command(cmd, 
                                                    self.host.ssh2['user'], 
                                                    self.host.ssh2['pwd'])
            if len(res['stderr']) > 0:
                raise RemoteExcpetion(res['stderr'])
            else:
                return True
        except RemoteExcpetion as ex:
            raise EmperorManagerExcpetion('Error starting new emperor istance: '+str(ex))

    def stop(self):
        '''
        Stop emperor istance on a remote portal2
        uwsgi --stop run/emperor.pid
        '''
        if self.check == None:
            self.check_environment()
            
        if self.check['uwsgi'] == None:
            raise EmperorManagerExcpetion('uwsgi is not installed')        
        
        try:
            cmd = 'cd %s && %s --stop %s/%s.pid' % (self.uwsgiPath, 
                                                    self.uwsgiExec, 
                                                    self.pidDir, 
                                                    self.name)
            res = self.remoteClient.run_ssh_command(cmd, 
                                                    self.host.ssh2['user'], 
                                                    self.host.ssh2['pwd'])
            if len(res['stderr']) > 0:
                raise RemoteExcpetion(res['stderr'])
            else:
                return True
        except RemoteExcpetion as ex:
            raise EmperorManagerExcpetion('Error stopping new emperor istance: '+str(ex))
    
    def reload(self):
        '''
        Reload emperor istance on a remote portal2
        uwsgi --reload run/emperor.pid
        '''
        if self.check == None:
            self.check_environment()
            
        if self.check['uwsgi'] == None:
            raise EmperorManagerExcpetion('uwsgi is not installed')        
        
        try:
            cmd = 'cd %s && %s --reload %s/%s.pid' % (self.uwsgiPath, 
                                                      self.uwsgiExec, 
                                                      self.pidDir, 
                                                      self.name)   
            res = self.remoteClient.run_ssh_command(cmd, 
                                                    self.host.ssh2['user'], 
                                                    self.host.ssh2['pwd'])
            if len(res['stderr']) > 0:
                raise RemoteExcpetion(res['stderr'])
            else:
                return True
        except RemoteExcpetion as ex:
            raise EmperorManagerExcpetion('Error reloading new emperor istance: '+str(ex))            