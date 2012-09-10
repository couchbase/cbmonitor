#!/usr/bin/env python

import json
import logging
import os
import re
import sys

"""Helper functions which can recursively traverse or visit couchbase
   REST / management data, driven by metadata.  Users can change
   behavior by passing in different visitor callback functions."""

def visit_dict(root, parents, data, meta, coll, level=0,
               up_key=None, up_data=None, up_coll=None):
    """Invoked when data is a dict."""
    if not isinstance(data, dict):
        log(data, " is not a dict")
        return
    next_level = level + 1
    for key in sorted(data.keys(), cmp=lambda x, y: cmp(hyphen_last(x),
                                                        hyphen_last(y))):
        val = data[key]
        meta_val = meta.get(key, None)
        if meta_val is None:
            log("warning: missing metadata entry at: %s; key: %s" %
                (parents, key))
            continue
        meta_inf = meta.get("-" + key, None)
        visit_entry(root, parents, data, meta, coll,
                    key, val, meta_val, meta_inf, level=next_level)

def visit_list(root, parents, data, meta, coll, level=0,
               up_key=None, up_data=None, up_coll=None):
    """Invoked when data is a list."""
    if not isinstance(data, list):
        log(data, " is not a list")
        return
    next_level = level + 1
    if len(meta) <= 0:
        log("warning: missing list metadata entry at: %s" % (parents))
        return
    meta_val = meta[0] # Use only the first item for metadata.
    for idx, val in enumerate(data):
        visit_entry(root, parents, data, meta, coll,
                    idx, val, meta_val, None, level=next_level)

"""Callbacks when visiting collections of different types.
"""
VISIT_COLLECTION_FUNCS = {"<type 'dict'>": visit_dict,
                          "<type 'list'>": visit_list}

def visit_url(context, path):
    """Recursively visits the JSON response from a URL, driven by metadata
       to follow links and process data."""
    root = dict(context) # Makes a copy.
    root["run"] = {}
    root["run"]["data"] = root["retrieve_funcs"]["retrieve_data"](context, path)
    root["run"]["meta"] = root["retrieve_funcs"]["retrieve_meta"](context, path)
    root["run"]["coll"] = type(root["run"]["meta"])() # Collection/hiearchy of slow data.
    root["run"]["tot_fast"] = 0
    root["run"]["tot_slow"] = 0
    func = root["collection_funcs"][str(type(root["run"]["meta"]))]
    func(root, [],
         root["run"]["data"],
         root["run"]["meta"],
         root["run"]["coll"])
    return root

EMIT_NONE = 0x00
EMIT_SLOW = 0x01
EMIT_FAST = 0x02

def visit_entry_default(root, parents, data, meta, coll,
                        key, val, meta_val, meta_inf, level=0,
                        emit_kind=None):
    """Records a scalar entry into the either the slow-changing or
       fast-changing time-series DB, depending on the emit_kind param.
       Recurses via visit_dict() or visit_list() to handle non-scalar entry."""
    path = parents + [str(key)]
    prefix = "  " * level

    t = type(val)
    if t != type(meta_val):
        if type(meta_val) == float or type(meta_val) == int:
            val = type(meta_val)(val)
        else:
            log("warning: unexpected type: %s; expected %s; at: %s" %
                (t, type(meta_val), path))
            return

    if t == str or t == unicode: # Scalar string entry.
        if emit_kind is None:
            emit_kind = EMIT_SLOW
        if emit_kind & EMIT_SLOW:
            debug(prefix, key, '=', '"%s"' % val)
            root["store"]["slow"](root, parents, data, meta, coll,
                                  key, val, meta_val, meta_inf, level)

            # Handle follow metadata, when val is URL/URI,
            # by pushing work onto the to-be-visited queue.
            if meta_inf and meta_inf.get('follow', None):
                context = dict(root) # Copy the context for recursion.
                del context["run"]   # But, not the current run info.
                root["queue"].append((context, val))

    elif t == float or t == int: # Scalar numeric entry.
        if emit_kind is None:
            emit_kind = EMIT_FAST
        if emit_kind & EMIT_FAST:
            units = ''
            if meta_inf:
                units = meta_inf.get("units", '')
            debug(prefix, "ns-" + '-'.join(path), '=', val, units)
            root["store"]["fast"](root, parents, data, meta, coll,
                                  key, val, meta_val, meta_inf, level)
        if emit_kind & EMIT_SLOW:
            debug(prefix, key, '=', val)
            root["store"]["slow"](root, parents, data, meta, coll,
                                  key, val, meta_val, meta_inf, level)

    elif t == bool: # Scalar boolean entry.
        if emit_kind is None:
            emit_kind = EMIT_SLOW
        if emit_kind & EMIT_FAST:
            debug(prefix, "ns-" + '-'.join(path), '=', int(val))
            root["store"]["fast"](root, parents, data, meta, coll,
                                  key, val, meta_val, meta_inf, level)
            root["run"]["tot_fast"] += 1
        if emit_kind & EMIT_SLOW:
            debug(prefix, key, '=', val)
            root["store"]["slow"](root, parents, data, meta, coll,
                                  key, val, meta_val, meta_inf, level)

    elif t == dict or t == list: # Non-scalar entry.
        child_coll = t()
        debug(prefix, key, "= ...")
        if type(coll) == dict:
            coll[key] = child_coll
        else:
            coll.append(child_coll)
        func = root["collection_funcs"][str(t)]
        func(root, path, val, meta_val, child_coll, level=level,
             up_key=key, up_data=data, up_coll=coll)
    else:
        log("warning: unhandled type for val: %s; in key: %s" % (val, key))

def visit_entry_fast(root, parents, data, meta, coll,
                     key, val, meta_val, meta_inf, level=0):
    """Records a scalar entry into the fast-changing time-series DB."""
    return visit_entry_default(root, parents, data, meta, coll,
                               key, val, meta_val, meta_inf, level=level,
                               emit_kind=EMIT_FAST)

def visit_entry_slow(root, parents, data, meta, coll,
                     key, val, meta_val, meta_inf, level=0):
    """Records a scalar entry into the slow-changing time-series DB."""
    return visit_entry_default(root, parents, data, meta, coll,
                               key, val, meta_val, meta_inf, level=level,
                               emit_kind=EMIT_SLOW)

def visit_entry_int(root, parents, data, meta, coll,
                    key, val, meta_val, meta_inf, level=0):
    """Parse the val as an int, and then use default processing."""
    return visit_entry_default(root, parents, data, meta, coll,
                               key, int(val), int(meta_val), meta_inf, level=level)

def visit_entry_strip(root, parents, data, meta, coll,
                      key, val, meta_val, meta_inf, level=0):
    """This visit_entry_func strips the entry from results."""
    return

def visit_entry_collect_mc_stats(root, parents, data, meta, coll,
                                 key, val, meta_val, meta_inf, level=0):
    """A different implementation could collects memcached stats from the
       val, which should be an array of "HOST:PORT", like
       ["couchbase-01:11210, couchbase-02:11211"].  The root and
       parents path should have bucket and SASL auth info.
       Use the main(entry_funcs) parameter to specify your own implementation."""
    debug("  " * level, "MC-STATS", val)

def visit_entry_collect_proxy_stats(root, parents, data, meta, coll,
                                    key, val, meta_val, meta_inf, level=0):
    """A different implementation could collects proxy stats from the
       val, which should be a port number (like 11211).  The hostname
       should be amongst the ancestors."""
    debug("  " * level, "PROXY-STATS", val)

"""Callbacks when visiting scalar values, driven by 'visit' metadata.
"""
VISIT_ENTRY_FUNCS = {"default": visit_entry_default,
                     "fast": visit_entry_fast,
                     "slow": visit_entry_slow,
                     "int": visit_entry_int,
                     "strip": visit_entry_strip,
                     "collect_mc_stats": visit_entry_collect_mc_stats,
                     "collect_proxy_stats": visit_entry_collect_proxy_stats}

def visit_entry(root, parents, data, meta, coll,
                key, val, meta_val, meta_inf, level=0):
    """Invokes the right visit_entry_func on an entry."""
    if (type(key) == str or type(key) == unicode) and key.startswith('-'):
        if root.get("strip_meta", True):
            return

    if meta_inf:
        visit = meta_inf.get("visit", "default")
    else:
        visit = "default"

    visit_entry_func = root["entry_funcs"].get(visit)
    if not visit_entry_func:
        sys.exit("error: unknown visit function: %s; at %s" %
                 (meta_inf["visit"], parents + [key]))

    return visit_entry_func(root, parents, data, meta, coll,
                            key, val, meta_val, meta_inf, level=level)

def retrieve_data(context, path):
    """This simple implementation for testing just pretends that metadata
       is data."""
    return retrieve_meta(context, path)

def retrieve_meta(context, path):
    """Retrieves the parsed json metadata that corresponds to
       the given parts of an ns_server URL.
       A path can look like '/pools/default?not=used&ignored=yes'."""
    with open(meta_path(context, path)) as f:
        return json.loads(f.read())

"""Functions used when visit needs to retrieve data, metadata, etc.
"""
VISIT_RETRIEVE_FUNCS = {"retrieve_data": retrieve_data,
                        "retrieve_meta": retrieve_meta}

def meta_path(context, path):
    """Calculates the path of the metadata JSON file given a data/URL path."""
    path = path.split('?')[0]
    path = re.sub("/buckets/[^/]+/", "/buckets/BUCKET/", path)
    path = re.sub("/buckets/[^/]+$", "/buckets/BUCKET", path)
    path = re.sub("/nodes/[^/]+/", "/nodes/HOST%3APORT/", path)
    path = re.sub("/nodes/[^/]+$", "/nodes/HOST%3APORT", path)
    fname = os.path.dirname(__file__) \
            + "/ns_server/2.0.0/%s.json" % (path[1:].replace("/", "_"))
    return fname

def log(*args):
    logging.debug(" ".join([str(x) for x in args]))

def debug(*args):
    return

def hyphen_last(s):
    """Converts '-foo' to 'foo-', so that 'foo-' comes after 'foo'
       which is useful for sorting."""
    if s.startswith('-'):
        return s[1:] + '-'
    return s

def store_fast(root, parents, data, meta, coll,
               key, val, meta_val, meta_inf, level):
    """Instead of this sample callback, a real implementation would store
       numeric or boolean metric into fast-changing time-series DB."""
    root["run"]["tot_fast"] += 1

def store_slow(root, parents, data, meta, coll,
               key, val, meta_val, meta_inf, level):
    """Example callback when visit encounters a slow-changing value."""
    coll[key] = val
    root["run"]["tot_slow"] += 1

def url_before(context, path):
    """Example callback invoked by visit() on a new URL."""
    log("=====", path)
    return context, path

def url_after(context, path, root):
    """Example callback invoked by visit() after visiting a URL."""
    log("tot_fast =", root["run"]["tot_fast"])
    log("-----", path)
    log(json.dumps(root["run"]["coll"], sort_keys=True, indent=4))

def visit_queue(queue):
    """Visits all the URL's on a queue, potentially concurrently."""
    while queue:
        context, path = queue.pop()
        if (context.get("ctl") or {}).get("stop"):
            return context.get("ctl").get("stop")
        context, path = context["callbacks"]["url_before"](context, path)
        root = visit_url(context, path)
        context["callbacks"]["url_after"](context, path, root)

# ----------------------------------------------------------------

def main(host, port, path, store, callbacks,
         collection_funcs=VISIT_COLLECTION_FUNCS,
         retrieve_funcs=VISIT_RETRIEVE_FUNCS,
         entry_funcs=VISIT_ENTRY_FUNCS,
         strip_meta=True, ctl=None, queue=None):
    """The ease-of-use entry-point to start a recursive URL visit()."""
    context = make_context(host, port, path, store, callbacks,
                           collection_funcs=collection_funcs,
                           retrieve_funcs=retrieve_funcs,
                           entry_funcs=entry_funcs,
                           strip_meta=strip_meta, ctl=ctl, queue=queue)
    context["queue"].append((context, path))
    return visit_queue(context["queue"])

def make_context(host, port, path, store, callbacks,
                 collection_funcs, retrieve_funcs, entry_funcs,
                 strip_meta, ctl, queue):
    """Returns a context object which is passed around by visit()."""
    return {"host": host, "port": port, "store": store,
            "path": path, "queue": queue or [], "ctl": ctl,
            "collection_funcs": collection_funcs,
            "retrieve_funcs": retrieve_funcs,
            "entry_funcs": entry_funcs,
            "strip_meta": strip_meta,
            "callbacks": callbacks}

if __name__ == '__main__':
    main("127.0.0.1", 8091, "/pools/default",
         {"fast": store_fast,
          "slow": store_slow},
         {"url_before": url_before,
          "url_after": url_after})

