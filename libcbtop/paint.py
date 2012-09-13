#!/usr/bin/env python
"""
- Paint the table on:

    - blessings terminal (http://pypi.python.org/pypi/blessings)

- Callbacks for tabula package to format a value based on its meta.
"""

import logging
from blessings import Terminal
from tabula.table import Table

UNITS_SUFFIX = ["", "K", "M", "G", "T"]

term = Terminal()

def conv_units(val, meta):
    """
    Callback function for tabula

    Format and convert units to be more human readable

    @return new val with converted units
    """
    if not val or not meta:
        return val

    try:
        val = float(val)
    except ValueError:
        logging.error("unable to apply convert units for %s" % val)
        return val

    suf = 0
    if meta in ["bytes", "items"]:

        while val > 1024 and suf < 4:
            val /= 1024
            suf += 1
        return "%.2f%s" % (val, UNITS_SUFFIX[suf])

    return "%.2f" % val

TABULA_META_FUNCS = {"units": conv_units}

def enter_fullscreen():
    """
    Invoke before printing out anything.
    This method should be replaced by or merged to blessings package
    """
    term.stream.write(term.enter_fullscreen)
    term.stream.write(term.hide_cursor)

def exit_fullscreen():
    """
    Invoke before printing out anything.
    This method should be replaced by or merged to blessings package
    """
    term.stream.write(term.exit_fullscreen)
    term.stream.write(term.normal_cursor)

def paint(tbl):
    """
    Paint the table on terminal
    """
    if not isinstance(tbl, Table):
        logging.error("unable to paint table: invalid object")
        return False

    term.stream.write(term.clear)

    term.stream.write(str(tbl))
    return True