# -*- encoding: utf8 -*-

import json
import logging
import logging.config
import logging.handlers

import requests

from app import exception

__author__ = "Nilson Lopes"

logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'datetime': {
            'format': ('%(asctime)s %(levelname)s '
                       '%(name)s:%(lineno)d %(message)s'),
        },
    },
    'handlers': {
        'file': {
            'class': 'logging.FileHandler',
            'formatter': 'datetime',
            'level': 'DEBUG',
            'filename': 'scheduler.log',
        },
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
            'stream': 'ext://sys.stdout',
        },
    },
    'loggers': {
        '': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
})


class BaseAPI(object):
    """Basic scheduller API class
    """

    def __init__(self, auth_token):
        self.auth_token = auth_token
        self.end_point = "http://intranet.sccit.local/2/schedule-api"
        self.logger = logging.getLogger(__name__)

    def send_post(self, payload):
        headers = {'SCC-API-Key': self.auth_token,
                   'Content-Type': 'application/json'}
        try:
            response = requests.post(self.end_point,
                                     data=json.dumps(payload),
                                     headers=headers, verify=False)
            if response.status_code == 401:
                raise exception.APIError(
                    'Authentication to the server failed')
            data = json.loads(response.content)
        except (requests.ConnectionError, requests.ConnectTimeout) as ex:
            raise exception.APIError(str(ex), ex) from ex
        except requests.exceptions.RequestException as ex:
            raise exception.APIError(
                'Unable to connect to "%s"' % self.end_point) from ex
        except json.JSONDecodeError as ex:
            raise exception.APIError(
                'Server response from %s is not json' % self.end_point) from ex

        if data['status'].lower() == "error":
            raise exception.APIError(data['message'])
        return data
