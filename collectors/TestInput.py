"""
Testrunner (cbtestlib) legacy
"""


class TestInputSingleton(object):
    input = None


class TestInput(object):

    def __init__(self):
        self.servers = []
        self.moxis = []
        self.clusters = {}
        self.membase_settings = None
        self.test_params = {}

    def param(self, name, default_value):
        if name in self.test_params:
            return self._parse_param(self.test_params[name])
        else:
            return default_value

    @staticmethod
    def _parse_param(value):
        try:
            return int(value)
        except ValueError:
            pass

        try:
            return float(value)
        except ValueError:
            pass

        if value.lower() == "false":
            return False
        if value.lower() == "true":
            return True
        return value


class TestInputServer(object):

    def __init__(self):
        self.ip = ''
        self.ssh_username = ''
        self.ssh_password = ''
        self.ssh_key = ''
        self.rest_username = ''
        self.rest_password = ''
        self.port = ''
        self.cli_path = ''
        self.data_path = ''

    def __str__(self):
        ip_str = "ip:{0} port:{1}".format(self.ip, self.port)
        ssh_username_str = "ssh_username:{0}".format(self.ssh_username)
        return "{0} {1}".format(ip_str, ssh_username_str)

    def __repr__(self):
        ip_str = "ip:{0} port:{1}".format(self.ip, self.port)
        ssh_username_str = "ssh_username:{0}".format(self.ssh_username)
        return "{0} {1}".format(ip_str, ssh_username_str)
