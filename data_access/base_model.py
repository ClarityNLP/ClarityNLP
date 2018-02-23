import json


class BaseModel(object):
    def to_json(self):
        return json.dumps(self.__dict__, indent=4)

    @classmethod
    def from_json(cls, string: str):
        obj = json.loads(string)
        return cls(**obj)

    @classmethod
    def from_dict(cls, obj: dict):
        return cls(**obj)
