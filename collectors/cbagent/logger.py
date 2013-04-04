import logging
import logging.config
import sys
import types

DICT_CONFIG = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'default': {
            'format': '%(asctime)s %(levelname)s - %(message)s',
            'datefmt': '[%d/%b/%Y %H:%M:%S]'
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'default',
        }
    },
    'loggers': {
        '': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        }
    }
}

logging.config.dictConfig(DICT_CONFIG)
logger = logging.getLogger()


def error(self, msg, *args, **kwargs):
    self.error(msg, *args, **kwargs)
    sys.exit(1)

logger.interrupt = types.MethodType(error, logger)
