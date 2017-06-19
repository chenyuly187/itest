# -*- coding: utf-8 -*-
import os
import logging.config

# BASE_DIR
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# LOGGING
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s - %(levelname)s - %(pathname)s : %(message)s'
        },
    },
    'handlers': {
        'file_handler': {
            'level': 'DEBUG',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': '%s/log/itest.log' % BASE_DIR,
            'formatter': 'standard',
            'encoding': 'utf-8'
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
        }
    },
    'loggers': {
        'itest': {
            'handlers': ['file_handler', 'console'],
            'level': 'DEBUG',
            'propagate': True
        }
    }
}
logging.config.dictConfig(LOGGING)
