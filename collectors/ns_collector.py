import time

from cbagent.collectors import NSServer
from cbagent.settings import Settings


def main():
    settings = Settings()
    settings.read_cfg()

    ns_collector = NSServer(settings)
    if settings.update_metadata:
        ns_collector.update_metadata()

    while True:
        try:
            ns_collector.collect()
            time.sleep(settings.interval)
        except KeyboardInterrupt:
            break

if __name__ == '__main__':
    main()
