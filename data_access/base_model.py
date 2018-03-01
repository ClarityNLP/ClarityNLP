import json


class BaseModel(object):
    def to_json(self):
        return json.dumps(self.__dict__, indent=4)

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
