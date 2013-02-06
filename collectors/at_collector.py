import time

from cbagent.collectors import ActiveTasks
from cbagent.settings import Settings


def main():
    settings = Settings()
    settings.read_cfg()

    active_tasks = ActiveTasks(settings)
    if settings.update_metadata:
        active_tasks.update_metadata()

    while True:
        try:
            active_tasks.collect()
            time.sleep(settings.interval)
        except KeyboardInterrupt:
            break

if __name__ == '__main__':
    main()
