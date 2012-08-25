#!/usr/bin/env python

import logging
import numpy as np

class Section(object):
    """
    A section appears on the @class Table
    """
    def __init__(self, name, width, height, sep):
        self.name = name
        self.width = width          # max width
        self.height = height        # max height
        self.sep = sep

    def __repr__(self):
        raise NotImplementedError

    def _format(self):
        """
        Format the section to a presentable string

        @return (formatted string, viewable width, viewable height)
        """
        raise NotImplementedError

    def __str__(self):
        return self._format()[0]

    def size(self):
        """
        Return the viewable size of the section as @tuple (width, height)
        """
        return self._format()[1:]

class FlatSection(Section):
    """
    - Flat section:
        key1: val1, key2: val2
        key3: val3 ...
    """
    def __init__(self, name="", width=800, height=600, sep=":"):
        self.arr = {}
        super(FlatSection,self).__init__(name, width, height, sep)

    def __repr__(self):
        return "FlatSection(name=%r, width=%r, height=%r, "\
                "sep=%r, arr=%r)"\
                % (self.name, self.width, self.height,
                   self.sep, self.arr)

    def _format(self):
        if not self.arr:
            return "", 0, 0

        string = ""
        n_rows = 0
        cur = 0

        for key, val in self.arr.iteritems():

            key_val = "%s%s%s\t" % (key, self.sep, val)
            length = len(key_val)
            cur += length

            if cur > self.width:
                key_val = "\n" + key_val
                cur = length
                n_rows += 1

            string += key_val

        return string, self.width, n_rows

    def add_cell(self, key, val):
        self.arr[key] = val
        return True

    def del_cell(self, key):
        try:
            del self.arr[key]
        except KeyError:
            logging.error("unable to find key %s" % key)
            return False
        return True

    def get_cell(self, key):
        try:
            return self.arr[key]
        except KeyError:
            logging.error("unable to find key %s" % key)
            return None

class GridSection(Section):
    """
    - Grid section:
        Like a spreedsheet, with col and row headers

        name |  col1 |  col2
        row1 |  val1 |  val2
        row2 |  val3 |  val4
    """
    def __init__(self, name="", width=800, height=600, sep="|"):
        self.arr = None
        self.irt = {}       # inverted-row-table @dict {row_name: row_num}
        super(GridSection,self).__init__(name, width, height, sep)

    def __repr__(self):
        return "GridSection(name=%r, width=%r, height=%r, "\
                "sep=%r, arr=%r, irt=%r)"\
                % (self.name, self.width, self.height,
                   self.sep, self.arr, self.irt)

    def _format(self):
        if self.arr is None:
            return "", 0, 0

        # insert column headers
        ss = np.insert(self.arr, 0, self._get_col_hdrs(), 0)

        # TODO: align columns
        string = "\n".join(
                [self.sep.join(map(lambda x: str(x), row)) for row in ss])

#        string = np.array2string(ss, self.width, separator=self.sep)

        return string, self.width, len(ss)

    def add_cell(self, val, row, col, type="int32"):
        """
        Add/update a val on cell [row, col]

        Create new rows or columns accordingly

        @param row : row header name
        @param col : column header name
        """
        if self.arr is None:
            self.arr = np.array(
                [(row, val)], dtype=[ (self.name, "S16"), (col, type)])
            self.irt[row] = 0

        if not row in self._get_row_hdrs():
            self._expand_row(row)

        if not col in self._get_col_hdrs():
            self._expand_col(col, type)

        try:
            self._add_cell(val, row, col)
        except ValueError:
            logging.error("unable to add val %s to [%s,%s]: "\
                "not a compatible data type" % (val, row, col))
            return False

        return True

    def get_cell(self, row, col):
        #TODO
        raise NotImplementedError

    def add_row(self, name, vals):
        #TODO
        raise NotImplementedError

    def del_row(self, name):

        if self.arr is None:
            logging.error(
                "unable to delete row %s: empty section" % name)
            return False

        if not name in self._get_row_hdrs() or\
           not name in self.irt:
            logging.error(
                "unable to delete row %s: row doesn't exist" % name)
            return False

        row_num = self.irt[name]
        self.arr = np.delete(self.arr, row_num)
        self.irt.update(
            {k:v-1 for k,v in self.irt.iteritems() if v > row_num})

        return True

    def _get_col_hdrs(self):

        if self.arr is None:
            logging.error("unable to get row headers: empty section")
            return ()

        return self.arr.dtype.names

    def _get_row_hdrs(self):

        if self.arr is None:
            logging.error("unable to get row headers: empty section")
            return ()

        return self.arr[self.name]

    def _expand_col(self, name, type="int32"):

        if self.arr is None:
            logging.error(
                "unable to add column %s: empty section" % name)
            return False

        if name in self._get_col_hdrs():
            logging.error(
                "unable to add column %s: already exist" % name)
            return False

        new_dtype = self.arr.dtype.descr + [(name, type)]
        new_arr = np.zeros(self.arr.shape, dtype=new_dtype)

        for field in self.arr.dtype.fields:
            new_arr[field] = self.arr[field]

        return True

    def _expand_row(self, name):

        if self.arr is None:
            logging.error(
                "unable to add row %s: empty section" % name)
            return False

        if name in self._get_row_hdrs():
            logging.error(
                "unable to add row %s: already exist" % name)
            return False

        n_rows = len(self.arr)
        self.arr = np.insert(self.arr, n_rows, np.array([name,]), 0)

        self.irt[name] = n_rows

        return True

    def _add_cell(self, val, row, col):
        """
        @except ValueError : data type not compatible
        """
        if self.arr is None:
            logging.error(
                "unable to add value %s to [%s,%s]: empty section"
                % (val, row, col))
            return False

        if not row in self._get_row_hdrs() or\
            not row in self.irt:
            logging.error(
                "unable to add value %s to [%s,%s]: row doesn't exist"
                % (val, row, col))
            return False

        if not col in self._get_col_hdrs():
            logging.error(
                "unable to add value %s to [%s,%s]: column doesn't exist"
                % (val, row, col))
            return False

        self.arr[self.irt[row]][col] = val

        return True