import dataclasses
import datetime
import json


class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        if isinstance(o, datetime.date) or isinstance(o, datetime.time):
            return o.__str__()
        return super().default(o)
