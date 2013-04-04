import logging
import logging.config

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
