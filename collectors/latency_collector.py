import time

from cbagent.collectors import Latency
from cbagent.settings import Settings


def main():
    settings = Settings()
    settings.read_cfg()

    latency_collector = Latency(settings)
    if settings.update_metadata:
        latency_collector.update_metadata()

    while True:
        try:
            latency_collector.collect()
            time.sleep(settings.interval)
        except KeyboardInterrupt:
            break

if __name__ == '__main__':
    main()
