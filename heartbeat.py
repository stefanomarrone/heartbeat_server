import random

from chain import Chain, State
from pgmpy.models import MarkovChain
from pgmpy.factors.discrete import DiscreteFactor


class Heart:
    def __init__(self, chain: Chain):
        self.populate()
        self.states = chain.states
        self.current_state: State = random.choice(self.states)

    def beat(self):
        lo_bound = self.current_state.min
        hi_bound = self.current_state.max
        beat = random.uniform(lo_bound, hi_bound)
        self.current_state = self.transition()
        self.log(self.current_state)
        return beat

    def transition(self):
        transitions = self.get_transition_model().get(self.current_state.name, {})
        states, probs = zip(*transitions.items())
        next_state_name = random.choices(states, probs)[0]
        next_state = list(filter(lambda x: x.name == next_state_name), self.states)[0]
        return next_state

    def populate(self, chain: Chain):
        mmodel = MarkovChain()
        state_names = [state.name for state in chain.states]
        mmodel.add_nodes_from(state_names)
        for transition in chain.transitions:
            mmodel.add_edge(transition.from_state, transition.to_state)
        for transition in chain.transitions:
            factor = DiscreteFactor(
                variables=[transition.from_state, transition.to_state],
                cardinality=[2, 2],
                values=[1 - transition.rate, transition.rate, transition.rate, 1 - transition.rate]
            )
            mmodel.add_factors(factor)
        self.model = mmodel

    def log(self, state: State):
        print(f'next state is {state.name}')


