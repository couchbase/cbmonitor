class Store(object):

    def append(self, data, cluster=None, server=None, bucket=None,
               collector=None):
        raise NotImplementedError
