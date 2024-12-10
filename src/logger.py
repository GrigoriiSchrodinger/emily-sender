import json
import logging

import requests


class LokiHandler(logging.Handler):
    def __init__(self, url, tags):
        super().__init__()
        self.url = url
        self.tags = tags

    def emit(self, record):
        log_entry = self.format(record)
        tags_with_level = {
            **self.tags,
            "level": record.levelname,
            "module": record.module,
            "function": record.funcName,
            "time": record.created
        }

        payload = {
            "streams": [
                {
                    "stream": tags_with_level,
                    "values": [
                        [str(int(record.created * 1e9)), log_entry]
                    ]
                }
            ]
        }
        headers = {'Content-Type': 'application/json'}
        try:
            response = requests.post(self.url, data=json.dumps(payload), headers=headers)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Failed to send log to Loki: {e}, Response: {getattr(e.response, 'text', 'No response')}")


logger = logging.getLogger("Sender")
logger.setLevel(logging.DEBUG)

loki_handler = LokiHandler(
    url="http://localhost:3100/loki/api/v1/push",
    tags={"project": "Sender"},
)
logger.addHandler(loki_handler)
