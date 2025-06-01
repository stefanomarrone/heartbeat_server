from pydantic import BaseModel, field_validator, model_validator
from typing import List, Tuple
from collections import defaultdict

class ChainState(BaseModel):
    name: str
    min: float
    max: float

class ChainTransition(BaseModel):
    from_state: str
    to_state: str
    rate: float

class Chain(BaseModel):
    states: List[ChainState]
    transitions: List[ChainTransition]

    @model_validator(mode="after")
    def validate_chain(self):
        state_names = {state.name for state in self.states}
        # 1. Check that all from_state and to_state exist in states
        for t in self.transitions:
            if t.from_state not in state_names:
                raise ValueError(f"Transition from unknown state: {t.from_state}")
            if t.to_state not in state_names:
                raise ValueError(f"Transition to unknown state: {t.to_state}")
        # 2. Check for duplicate (from_state, to_state) pairs
        seen_pairs: set[Tuple[str, str]] = set()
        for t in self.transitions:
            key = (t.from_state, t.to_state)
            if key in seen_pairs:
                raise ValueError(f"Duplicate transition found: {key}")
            seen_pairs.add(key)
        # 3. Ensure transition rates from each state sum to 1.0
        rate_sums = defaultdict(float)
        for t in self.transitions:
            rate_sums[t.from_state] += t.rate
        for state, total in rate_sums.items():
            if abs(total - 1.0) > 1e-6:
                raise ValueError(f"Transition rates from '{state}' sum to {total}, expected 1.0")
        return self
