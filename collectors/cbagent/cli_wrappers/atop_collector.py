from cbagent.collectors import Atop
from cbagent.settings import Settings


def main():
    settings = Settings()
    settings.read_cfg()

    collector = Atop(settings)
    if settings.update_metadata:
        collector.update_metadata()
    collector.restart()
    collector.update_columns()
    collector.collect()

if __name__ == '__main__':
    main()
