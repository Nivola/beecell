# SPDX-License-Identifier: EUPL-1.2
#
# (C) Copyright 2018-2024 CSI-Piemonte


def group(rows, pos, maxpos):
    """ """
    vals = {}
    if pos < maxpos:
        for row in rows:
            try:
                vals[row[pos]].append(row)
            except:
                vals[row[pos]] = [row]
        for key, item in vals.items():
            vals[key] = group(item, pos + 1, maxpos)

        return vals
    else:
        return "//".join(rows[0])


def compact(vals):
    """ """
    if "*" in vals.keys():
        return explore(vals["*"])
    elif type(list(vals.values())[0]) in [str, bytes]:
        return list(vals.values())
    else:
        res = []
        for key, item in vals.items():
            data = compact(item)
            if type(data) is not list:
                res.append(data)
            else:
                res.extend(data)

        return res


def explore(data):
    if type(data) is dict:
        return explore(data["*"])
    else:
        return data


def extract(perms):
    """Reduce the permissions to a non redundant list.

    :param perms list: List like ['a1.b1.c4.*', 'a1.b1.c1.*', 'a1.b1.c2.*', 'a1.b2.*.*', 'a2.b3.*.*', 'a2.b4.c3.d1',
                                  'a2.*.*.*']
    :return: list like ['a1.b1.c2.*', 'a1.b1.c1.*', 'a1.b1.c4.*', 'a1.b2.*.*', 'a2.*.*.*']
    """
    rows = [r.split("//") for r in perms]
    vals = group(rows, 0, len(perms[0].split("//")))
    res = compact(vals)
    if type(res) is str or type(res) is bytes:
        res = [res]
    return res
