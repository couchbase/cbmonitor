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

    def handle(self, data):
        """
        wrap the data into a json doc
        dump to current directory
        """
        if not data:
            logging.error("unable to handle : invalid data")
            return False

        if not self.filename:
            self.filename = "unknown.json"

        with open(self.filename, "w") as f:
            f.write(json.dumps(data))

        return True