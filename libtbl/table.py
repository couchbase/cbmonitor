#!/usr/bin/env python

import logging
import numpy as np
from section import Section

class Table(object):
    """
    A table contains several @class Section

    - Horizontal view

        section-1
        ---------
        section-2
        ---------
        section-3
    """
    def __init__(self, name="", width=800, height=600, sep="-"):
        self.name = name
        self.width = width          # max width
        self.height = height        # max height
        self.sep = sep
        self.sections = {}          # @dict {name: @class Section}
        self.hori = True

    def __str__(self):
        div = "\n%s\n" % (self.sep * self.size()[0])
        return div.join(
            map(lambda x: str(x), self.sections.itervalues()))

    def __repr__(self):
        return "Table(name=%r, sections=%r, hori=%r)"\
            % (self.name, self.sections, self.hori)

    def size(self):
        """Return the viewable size of the Table as @tuple (x,y)"""
        width = max(
            map(lambda x: x.size()[0], self.sections.itervalues()))

        height = sum(
            map(lambda x: x.size()[1], self.sections.itervalues()))

        return width, height

    def add_section(self, section):
        if isinstance(section, Section):
            self.sections[section.name] = section