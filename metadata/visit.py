#!/usr/bin/env python

import json
import re
import sys

def visit_dict(root, parents, data, meta, coll, level=0):
    """Invoked when data is a dict."""
    next_level = level + 1
    for key, val in data.iteritems():
        meta_val = meta.get(key, None)
        if meta_val is None:
            log("warning: missing metadata entry at: %s; key: %s" %
                (parents, key))
            continue
        meta_inf = meta.get("-" + key, None)
        visit_entry(root, parents, data, meta, coll,
                    key, val, meta_val, meta_inf, level=next_level)

def visit_list(root, parents, data, meta, coll, level=0):
    """Invoked when data is a list."""
    next_level = level + 1
    if len(meta) <= 0:
        log("warning: missing list metadata entry at: %s" % (parents))
        return
    meta_val = meta[0] # Use only the first item for metadata.
    for idx, val in enumerate(data):
        visit_entry(root, parents, data, meta, coll,
                    idx, val, meta_val, None, level=next_level)

VISIT_CONTAINER_FUNCS = {"<type 'dict'>": visit_dict,
                         "<type 'list'>": visit_list}

def visit_url(context, path):
    """Recursively visits a ns_server URL, driven by metadata
       to follow links and process data."""
    root = dict(context) # Makes a copy.
    root["run"] = {}
    root["run"]["data"] = retrieve_data(context, path)
    root["run"]["meta"] = retrieve_meta(context, path)
    root["run"]["coll"] = type(root["run"]["meta"])() # Collection/hiearchy of slow data.
    root["run"]["tot_fast"] = 0
    root["run"]["tot_slow"] = 0
    func = VISIT_CONTAINER_FUNCS[str(type(root["run"]["meta"]))]
    func(root, [],
         root["run"]["data"],
         root["run"]["meta"],
         root["run"]["coll"])
    log("tot_fast =", root["run"]["tot_fast"])
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
    if (type(key) == str or type(key) == unicode) and key[0] == '-':
        return

    path = parents + [str(key)]
    prefix = "  " * level

    t = type(val)
    if t != type(meta_val):
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
            # by pushing work onto the todo queue.
            if meta_inf and meta_inf.get('follow', None):
                context = dict(root) # Copy the context for recursion.
                del context["run"]   # But, not the current run info.
                root["todo"].append((context, val))

    elif t == float or t == int: # Scalar numeric entry.
        if emit_kind is None:
            emit_kind = EMIT_FAST

        if emit_kind & EMIT_FAST:
            units = ''
            if meta_inf:
                units = meta_inf.get("units", '')
            log(prefix, "ns-" + '-'.join(path), '=', val, units)
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
            log(prefix, "ns-" + '-'.join(path), '=', int(val))
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

        func = VISIT_CONTAINER_FUNCS[str(t)]
        func(root, path, val, meta_val, child_coll, level=level)

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
    """Collects memcached stats from the val, which should be an array
       of "HOST:PORT", like ["couchbase-01:11210, couchbase-02:11211"].
       The root and parents path should have bucket and SASL auth info."""
    log("  " * level, "MC-STATS", val)
    return # TODO.

VISIT_ENTRY_FUNCS = {"default": visit_entry_default,
                     "fast": visit_entry_fast,
                     "slow": visit_entry_slow,
                     "int": visit_entry_int,
                     "strip": visit_entry_strip,
                     "collect_mc_stats": visit_entry_collect_mc_stats}

def visit_entry(root, parents, data, meta, coll,
                key, val, meta_val, meta_inf, level=0):
    """Invokes the right visit_entry_func on an entry."""
    if (type(key) == str or type(key) == unicode) and key[0] == '-':
        return

    if meta_inf:
        visit = meta_inf.get("visit", "default")
    else:
        visit = "default"

    visit_entry_func = VISIT_ENTRY_FUNCS.get(visit)
    if not visit_entry_func:
        sys.exit("error: unknown visit function: %s; at %s" %
                 (meta_inf["visit"], parents + [key]))

    return visit_entry_func(root, parents, data, meta, coll,
                            key, val, meta_val, meta_inf, level=level)

def retrieve_data(context, path):
    # TODO: Fake implementation for now, since we can pretend
    # that a metadata file is actually a data result from ns_server.
    return retrieve_meta(context, path)

def retrieve_meta(context, path):
    """Retrieves the parsed json metadata that corresponds to
       the given parts of an ns_server URL.
       A path can look like '/pools/default?not=used&ignored=yes'."""
    path = path.split('?')[0]
    path = re.sub("/buckets/[^/]+/", "/buckets/BUCKET/", path)
    path = re.sub("/buckets/[^/]+$", "/buckets/BUCKET", path)
    path = re.sub("/nodes/[^/]+/", "/nodes/HOST%3APORT/", path)
    path = re.sub("/nodes/[^/]+$", "/nodes/HOST%3APORT", path)
    fname = "./ns_server/2.0.0/%s.json" % (path[1:].replace("/", "_"))
    with open(fname) as f:
        return json.loads(f.read())

def log(*args):
    print >> sys.stderr, " ".join([str(x) for x in args])

def debug(*args):
    return

def store_fast(root, parents, data, meta, coll,
               key, val, meta_val, meta_inf, level):
    # TODO: Store numeric or boolean metric into fast-changing time-series DB.
    root["run"]["tot_fast"] += 1

def store_slow(root, parents, data, meta, coll,
               key, val, meta_val, meta_inf, level):
    coll[key] = val
    root["run"]["tot_slow"] += 1

def main(host, port, path, store):
    todo = []
    todo.append(({"host": host, "port": port, "store": store, "todo": todo}, path))
    while todo:
        next = todo.pop()
        log("[fast] =====", next[1])
        root = visit_url(next[0], next[1])
        log("[slow] -----", next[1])
        log(json.dumps(root["run"]["coll"], sort_keys=True, indent=4))

if __name__ == '__main__':
    main("127.0.0.1", 8091, "/pools/default",
         {"fast": store_fast, "slow": store_slow})

