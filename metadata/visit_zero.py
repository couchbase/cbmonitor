#!/usr/bin/env python

import json
import visit

"""Visits metadata and emits cleansed versions where
   values are converted to zeros. By zero'ing out values,
   the metadata becomes more easily diff'able."""

def zero(val):
    t = type(val)
    if t == int:
        return 0
    elif t == float:
        return 0.0
    elif t == bool:
        return False
    elif t == str or t == unicode:
        if val.startswith('/'):
            return val.split('?')[0]
    return val

def store_zero_fast(root, parents, data, meta, coll,
                    key, val, meta_val, meta_inf, level):
    if type(coll) == list and key == len(coll):
        coll.append(zero(val))
    else:
        coll[key] = zero(val)
    root["run"]["tot_fast"] += 1

def store_zero_slow(root, parents, data, meta, coll,
                    key, val, meta_val, meta_inf, level):
    if type(coll) == list and key == len(coll):
        coll.append(zero(val))
    else:
        coll[key] = zero(val)
    root["run"]["tot_slow"] += 1

def url_zero_before(context, path):
    return context, path

def url_zero_after(context, path, root):
    print "----------", visit.meta_path(context, path)
    print json.dumps(root["run"]["coll"], sort_keys=True, indent=4)

if __name__ == '__main__':
    # Override the visit entry funcs to not strip any data.
    visit_entry_funcs = dict(visit.VISIT_ENTRY_FUNCS)
    visit_entry_funcs["strip"] = visit_entry_funcs["default"]

    visit.main("127.0.0.1", 8091, "/pools/default",
               {"fast": store_zero_fast,
                "slow": store_zero_slow},
               {"url_before": url_zero_before,
                "url_after": url_zero_after},
               entry_funcs=visit_entry_funcs,
               strip_meta=False)

