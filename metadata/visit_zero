#!/usr/bin/env python

import json
import visit

"""Visits ns_server metadata and emits cleansed versions where
   values are converted to zeros. By zero'ing out values,
   the metadata becomes more easily diff'able."""

def emit(level, *args):
    print " " * level + " ".join([str(x) for x in args])

def zero(val):
    """Converts values into string-ified, JSON-friendly zero values
       for easy diff'ability."""
    t = type(val)
    if t == int:
        return "0"
    elif t == float:
        return "0.0"
    elif t == bool:
        return "false"
    elif t == str or t == unicode:
        if val.startswith('/'):
            val = val.split('?')[0]
        return '"%s"' % val
    else:
        sys.exit("error: unhandled zero val: %s; which has type: %s" % (val, t))

def comma(data, coll, offset=1):
    """Helper function to add a comma suffix to a line, to meet JSON spec."""
    if data is None or coll is None:
        return ""
    if len(coll) >= len(data) - offset:
        return ""
    return ","

def store_zero_fast(root, parents, data, meta, coll,
                    key, val, meta_val, meta_inf, level):
    if type(coll) == list:
        emit(level, zero(val) + comma(data, coll))
        coll.append(zero(val))
    else:
        emit(level, ('"%s"' % (key)) + ': ' + str(zero(val)) + comma(data, coll))
        coll[key] = zero(val)
    root["run"]["tot_fast"] += 1

def store_zero_slow(root, parents, data, meta, coll,
                    key, val, meta_val, meta_inf, level):
    if type(coll) == list:
        emit(level, zero(val) + comma(data, coll))
        coll.append(zero(val))
    else:
        emit(level, ('"%s"' % (key)) + ': ' + str(zero(val)) + comma(data, coll))
        coll[key] = zero(val)
    root["run"]["tot_slow"] += 1

def visit_zero_dict(root, parents, data, meta, coll, level=0,
                    up_key=None, up_data=None, up_coll=None):
    if type(up_data) == dict:
        prefix = '"%s": ' % parents[-1]
    else:
        prefix = ''
    suffix = comma(up_data, up_coll, offset=0)
    emit(level, prefix + "{")
    visit.visit_dict(root, parents, data, meta, coll, level=level,
                     up_key=up_key, up_data=up_data, up_coll=up_coll)
    emit(level, "}" + suffix)

def visit_zero_list(root, parents, data, meta, coll, level=0,
                    up_key=None, up_data=None, up_coll=None):
    if type(up_data) == dict:
        prefix = '"%s": ' % parents[-1]
    else:
        prefix = ''
    suffix = comma(up_data, up_coll, offset=0)
    emit(level, prefix + "[")
    visit.visit_list(root, parents, data, meta, coll, level=level,
                     up_key=up_key, up_data=up_data, up_coll=up_coll)
    emit(level, "]" + suffix)

def url_zero_before(context, path):
    print "----------", visit.meta_path(context, path)
    return context, path

def url_zero_after(context, path, root):
    return

if __name__ == '__main__':
    visit_collection_funcs = {}
    visit_collection_funcs["<type 'dict'>"] = visit_zero_dict
    visit_collection_funcs["<type 'list'>"] = visit_zero_list

    # We override to not perform a real strip.
    visit_entry_funcs = dict(visit.VISIT_ENTRY_FUNCS)
    visit_entry_funcs["strip"] = visit_entry_funcs["default"]

    visit.main("127.0.0.1", 8091, "/pools/default",
               {"fast": store_zero_fast,
                "slow": store_zero_slow},
               {"url_before": url_zero_before,
                "url_after": url_zero_after},
               collection_funcs=visit_collection_funcs,
               entry_funcs=visit_entry_funcs,
               strip_meta=False)

