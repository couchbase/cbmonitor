#!/usr/bin/env python

import logging
import json
from handler import Handler

class JsonHandler(Handler):
    """
    Handler to dump data to a json file
    """
    def __init__(self, filename=""):
        self.filename = filename

    def handle(self, source):
        """Wrap data into json doc and dump to a file"""
        if not source or \
            not source.data:
            logging.error("unable to handle : invalid data")
            return False

        if not self.filename:
            self.filename = \
                source.__class__.__name__ + "-" \
                + source.server.ip.replace(".", "-") \
                + ".json"

        with open(self.filename, "w") as f:
            f.write(json.dumps(source.data))

        return True