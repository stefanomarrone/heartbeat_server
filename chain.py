from typing import List

from pydantic import BaseModel

class State(BaseModel):
    name: str
    min: float
    max: float

class Transition(BaseModel):
    from_state: str
    to_state: str
    rate: float

class Chain(BaseModel):
    states: List[State]
    transitions: List[Transition]

