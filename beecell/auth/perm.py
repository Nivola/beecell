'''
Created on Aug 12, 2014

@author: darkbk
'''
import logging
import pprint

def group(rows, pos, maxpos):
    """ """
    vals = {}
    if pos < maxpos:
        for row in rows:
            try:
                vals[row[pos]].append(row)
            except:
                vals[row[pos]] = [row]
        for key, item in vals.iteritems():
            vals[key] = group(item, pos+1, maxpos)
    
        return vals
    else:
        return '//'.join(rows[0])

def compact(vals):
    """ """
    if '*' in vals.keys():
        return explore(vals['*'])
    elif type(vals.values()[0]) in [str, unicode]:
        return vals.values()
    else:
        res = []
        for key, item in vals.iteritems():
            data = compact(item)
            if type(data) is not list:
                res.append(data)
            else:
                res.extend(data)

        return res
    
def explore(data):
    if type(data) is dict:
        return explore(data['*'])
    else:
        return data

def extract(perms):
    """Reduce the permissions to a non redundant list.
                  
    :param perms list: List like ['a1.b1.c4.*', 'a1.b1.c1.*', 'a1.b1.c2.*',
                                  'a1.b2.*.*', 'a2.b3.*.*', 'a2.b4.c3.d1', 
                                  'a2.*.*.*']
    :return: list like ['a1.b1.c2.*', 'a1.b1.c1.*', 'a1.b1.c4.*', 'a1.b2.*.*',
                        'a2.*.*.*']
    """
    logger = logging.getLogger('gibbon.util.perm')
    #logger.debug('Input permissions: %s' % perms)
    rows = [r.split('//') for r in perms]
    vals = group(rows, 0, len(perms[0].split('//')))
    #logger.debug('Grouped permissions: %s' % vals)
    res = compact(vals)
    if type(res) is str or type(res) is unicode:
        res = [res]
    #logger.debug('Output permissions: %s' % res)
    return res