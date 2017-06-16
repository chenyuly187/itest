# -*- coding: utf-8 -*-
import os
import logging.config
from utils.HTMLTestRunner import stdout_redirector, stderr_redirector

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
            'formatter': 'standard'
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
            # 'stream': stdout_redirector
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
