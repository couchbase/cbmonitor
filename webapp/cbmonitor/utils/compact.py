from logger import logger
from seriesly import Seriesly


def main():
    seriesly = Seriesly()
    all_dbs = seriesly.list_dbs()
    for i, db in enumerate(all_dbs, start=1):
        logger.info("{}/{}: {}".format(i, len(all_dbs), db.strip()))
        seriesly[db.strip()].compact()

if __name__ == "__main__":
    main()
