
import logging
import logging.handlers

class vbscoresHandler(logging.handlers.HTTPHandler):

    def __init__(self, api_key):
        self.api_key = api_key
        super().__init__('vb-scores.com', '/apiv1/logs.json', secure=True)

    def mapLogRecord(self, record):
        dict = record.__dict__
        dict['api_key'] = self.api_key
        return dict


def getLogger(name, level, api_key):
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(vbscoresHandler(api_key))
    return logger

