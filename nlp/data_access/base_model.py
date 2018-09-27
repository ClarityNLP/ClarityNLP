import simplejson as json


def is_empty(item):
    if item is None:
        return True

    t = type(item)
    if t is str or t is list or t is set:
        if len(item) > 0:
            return False
        else:
            return True

    if t is dict:
        if len(item.items()) > 0:
            return False
        else:
            return True

    return False


class BaseModel(object):

    def to_json(self):
        non_empty = {k: v for k, v in self.__dict__.items() if not is_empty(v)}
        return json.dumps(non_empty, indent=4, ignore_nan=True)

    @classmethod
    def from_json(cls, string: str):
        obj = json.loads(string, strict=False)
        return cls(**obj)

    @classmethod
    def from_dict(cls, obj: dict):
        return cls(**obj)

    def __getitem__(self, key):
        return self.__dict__[key]

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __delitem__(self, key):
        del self.__dict__[key]

    def __contains__(self, key):
        return key in self.__dict__

    def __len__(self):
        return len(self.__dict__)

    def __repr__(self):
        return repr(self.__dict__)


class NLPModel(BaseModel):

    def __init__(self, terms=None, text='', min_value='0', max_value='10000', case_sensitive=False):
        if terms is None:
            terms = list()
        self.terms = terms
        self.text = text
        self.min_value = min_value
        self.max_value = max_value
        self.case_sensitive = case_sensitive
