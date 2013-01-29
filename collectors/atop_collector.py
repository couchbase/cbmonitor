import time

from cbagent.collectors.atop import Atop

from cbagent.settings import Settings


def main():
    settings = Settings()

    atop_collector = Atop(settings)
    atop_collector.update_metadata()
    atop_collector.restart()
    atop_collector.update_columns()

    while True:
        try:
            atop_collector.collect()
            time.sleep(settings.interval)
        except KeyboardInterrupt:
            break

if __name__ == '__main__':
    main()
