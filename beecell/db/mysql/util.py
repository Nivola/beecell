'''
Created on Dec 6, 2013

@author: darkbk
'''
import time
from beecell.simple import run_command
from sqlalchemy.sql import compiler
from MySQLdb.converters import conversions, escape

def compile_query(query):
    dialect = query.session.bind.dialect
    statement = query.statement
    comp = compiler.SQLCompiler(dialect, statement)
    comp.compile()
    enc = dialect.encoding
    params = []
    for k in comp.positiontup:
        v = comp.params[k]
        if isinstance(v, unicode):
            v = v.encode(enc)
        params.append( escape(v, conversions) )
    return (comp.string.encode(enc) % tuple(params)).decode(enc)

def get_process_list():
    port = 3308
    host = '10.102.47.205'
    user = 'root'
    pwd = 'testlab'
    socket = '/var/lib/mysql2/mysql2.sock'
    cmd = ['mysql', '--port=%s' % port, '--host=%s' % host, '--protocol=tcp', 
           '--password=%s' % pwd, '--user=%s' % user,  
           '-e', 'show processlist\G']
    #cmd = ['mysql', '-S=%s' % socket, '--user=%s' % user,
    #       '-e', 'show processlist\G']
    res = run_command(cmd)
    
    # process exit correctly
    if res[0] == 0:
        process_list = []
        # spit data string into lines
        datas = res[1].split('\n')
        # remove last element = ' '
        datas.pop()
        # iter datas
        for data in datas:
            item = data.strip().split(':')
            # remove comment line
            if item[0].find('***') > -1:
                process_info = {}
            # first id of a new record
            elif item[0] == 'Id':
                process_info['id'] = int(item[1].strip())
                process_list.append(process_info)
            # populate ither fields of the current record
            #elif item[0] == 'Host':
            #    process_info[(item[0].lower())] = "%s:%s" % (item[1].strip(), 
            #                                                 int(item[2].strip()))        
            else:
                process_info[(item[0].lower())] = item[1].strip()
                
        return process_list
'''
i = 0
while True:
    process_list = get_process_list()
    for item in process_list:
        #print item
        if item['info'] != 'NULL' and item['info'] != 'show processlist':
            print "id: %-8s state: %-15s db: %-10s user: %-10s host: %-40s cmd: %-10s info: %s [%s]" % (
                item['id'], item['state'], item['db'], item['user'], item['host'], item['command'], item['info'], item['time'])
    i += 1
'''