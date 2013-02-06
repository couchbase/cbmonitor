import time

from cbagent.collectors import Atop

from cbagent.settings import Settings


def main():
    settings = Settings()
    settings.read_cfg()

    atop_collector = Atop(settings)

    if settings.update_metadata:
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
