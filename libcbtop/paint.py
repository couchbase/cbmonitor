#!/usr/bin/env python
"""
- Paint the table on:

    - blessings terminal (http://pypi.python.org/pypi/blessings)

- Callbacks for tabula package to format a value based on its meta.
"""

import logging
import ast

from blessings import Terminal
from tabula.table import Table

UNITS_SUFFIX = ["", "K", "M", "G", "T"]

term = Terminal()

STYLES = {"bold": term.bold,
          "reverse": term.reverse,
          "underline": term.underline,
          "blink": term.blink,
          "italic": term.italic,
          "shadow": term.shadow,
          "standout": term.standout,
          "subscript": term.subscript,
          "superscript": term.superscript,
          "flash": term.flash}

COLORS = {"red": term.red,
          "black": term.black,
          "green": term.green,
          "yellow": term.yellow,
          "blue": term.blue,
          "magenta": term.magenta,
          "white": term.white}

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

def change_style(val, meta):
    """
    Callback function for tabula

    Change style to display the value, for blessings terminal only

    Supported style: bold, reverse, underline, blink, normal, etc
    """
    if not val or not meta:
        return val

    if meta in STYLES:
        return STYLES[meta](val)

    return val

def change_color(val, meta):
    """
    Callback function for tabula

    Change color to display the value, for blessings terminal only
    """
    if not val or not meta:
        return val

    if meta in COLORS:
        return COLORS[meta](val)

    return val

def check_range(val, meta):
    """
    Callback function for tabula

    Check the range of acceptance defined in metadata
    and display error on screen

    Range is a str literal which evaluates to a @tuple or @list pair
    e.g - (10,100), [20,50]

    Value and edges are converted to float before comparison
    """
    if not val or not meta:
        return val

    try:
        f_val = float(val)
        f_min, f_max = map(lambda x: float(x), ast.literal_eval(meta))
    except (SyntaxError, ValueError), e:
        logging.error("unable to parse range string - %s: %s" % (meta, e))
        return val

    if f_val < f_min or f_val > f_max:
        return COLORS["red"](val)

    return val

"""
Functions to format a value using its meta,
which are called in alphabecial order.

TABULA_CONV_FUNCS: convert value before column alignments
TABULA_DECO_FUNCS: decorate value after column alignments
"""
TABULA_CONV_FUNCS = {"units": conv_units}

TABULA_DECO_FUNCS = {"style": change_style,
                     "color": change_color,
                     "range": check_range}

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