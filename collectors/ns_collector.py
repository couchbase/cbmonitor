import time

from cbagent.collectors.ns_server import NSServer
from cbagent.settings import Settings


def main():
    settings = Settings()

    ns_collector = NSServer(settings)
    ns_collector.update_metadata()

    while True:
        try:
            ns_collector.collect()
            time.sleep(settings.interval)
        except KeyboardInterrupt:
            break

if __name__ == '__main__':
    main()
