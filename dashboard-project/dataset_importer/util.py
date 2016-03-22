import json
from datetime import datetime, date
import dateutil.parser

class DatetimeEncoder(json.JSONEncoder):
    """
    A type of JSONEncoder that knows how to handle date and datetime
    objects. Serialises to a standard ISO format, which is 
    usable directly in JS.
    """
    
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%dT%H:%M:%SZ')
        elif isinstance(obj, date):
            return obj.strftime('%Y-%m-%d')
        # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, obj)

class DateTimeDecoder(json.JSONDecoder):

    def __init__(self, *args, **kargs):
        json.JSONDecoder.__init__(self, object_hook=self.dict_to_object, *args, **kargs)
    
    def dict_to_object(self, d):
        if isinstance(d["x"], basestring):
            try:
                dateobj = datetime.strptime(d["x"], "%Y-%m-%d")
                return {"y": d["y"], "x": dateobj}
            except (ValueError):
                try:
                    datetimeobj = dateutil.parser.parse(d["x"])
                    return {"y": d["y"], "x": datetimeobj}
                except (ValueError, AttributeError):
                    return d
        return d
        