from .base_model import BaseModel
from .pipeline_config import PipelineConfig
from typing import List


class PhenotypeModel(BaseModel):

    def __init__(self, owner: str, rules: List[str], pipelines: List[PipelineConfig]):
        self.owner = owner
        self.rules = rules
        self.pipelines = pipelines
