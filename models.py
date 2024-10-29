from pydantic import BaseModel
from typing import List

class RegistrabilityRequest(BaseModel):
    mark_name: str
    description: str
    selected_classes: List[str]
    request: str