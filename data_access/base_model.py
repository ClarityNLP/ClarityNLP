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


class NLPModel(BaseModel):

    def __init__(self, terms=[], text=''):
        self.terms = terms
        self.text = text
