import json
import unittest

from mock import patch

from cbagent.settings import DefaultSettings
from cbagent.collectors import NSServer


class CollectorMock(NSServer):

    def _get(self, path, *args, **kwargs):
        fname = 'collectors/fixtures/{0}.json'.format(path.replace('/', '_'))
        with open(fname) as fh:
            return json.loads(fh.read())


@patch('tests.NSServer', new=CollectorMock)
class CollectorTest(unittest.TestCase):

    @patch('cbagent.collectors.collector.MetadataClient', autospec=True)
    def test_ns_collector_update_metadata(self, md_mock):
        settings = DefaultSettings()
        ns_collector = NSServer(settings)
        ns_collector.update_metadata()
