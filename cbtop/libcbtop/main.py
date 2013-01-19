#!/usr/bin/env python

import logging
import time
import multiprocessing

from metadata.visit import main as visit, VISIT_ENTRY_FUNCS, retrieve_meta

import visit_cb as vc
import paint as pt

CTL = {"run_ok": True, "bg": True}

def main(server, itv=5, ctl=CTL, port=8091, path="/pools/default",
         dbhost="127.0.0.1", dbslow="slow", dbfast="fast"):

    vc.store = vc.SerieslyStore(dbhost, dbslow, dbfast)
    vc.tbl.set_ftr("Last Update: %time")
    if not ctl["bg"]:
        pt.enter_fullscreen()

    mc_store = vc.SerieslyStore(dbhost, dbslow, dbfast)

    mc_proc = multiprocessing.Process(target=vc.mc_worker,
        args=(vc.mc_jobs, vc.mc_stats,
              ctl, mc_store, itv))

    mc_proc.daemon = True
    mc_proc.start()

    visit_entry_func = VISIT_ENTRY_FUNCS.copy()
    visit_entry_func["collect_mc_stats"] = vc.collect_mc_stats

    while ctl["run_ok"]:

        vc.store.clear()
        visit(server, port, path,
                {"fast": vc.store_fast,
                 "slow": vc.store_slow},
                {"url_before": vc.url_before,
                 "url_after": vc.url_after},
            retrieve_funcs={"retrieve_data": vc.retrieve_data,
                            "retrieve_meta": retrieve_meta},
            entry_funcs=visit_entry_func, ctl=ctl)
        vc.store.persist()

        if not ctl["bg"]:
            pt.paint(vc.tbl)
        logging.info("sleep for %s seconds" % itv)
        time.sleep(itv)