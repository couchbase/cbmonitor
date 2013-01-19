#!/usr/bin/env python

class Server(object):

    def __init__(self, ip="127.0.0.1", port="8091",ssh_username="root",
                 ssh_password="coucbhase", ssh_key="",
                 rest_username="Administrator",rest_password="password",
                 data_path=""):
        self.ip = ip
        self.port = port
        self.ssh_username = ssh_username
        self.ssh_password = ssh_password
        self.ssh_key = ssh_key
        self.rest_username = rest_username
        self.rest_password = rest_password
        self.data_path = data_path

    def __repr__(self):
        return "<Server> ip: %s, port: %s, ssh_username: %s, "\
            "ssh_password: %s, ssh_key: %s, rest_username: %s, "\
            "rest_password: %s, data_path: %s" % \
            (self.ip, self.port, self.ssh_username, self.ssh_password,
             self.ssh_key, self.rest_username, self.rest_password,
             self.data_path)

    def __str__(self):
        return self.__repr__()