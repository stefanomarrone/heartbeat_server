import random
import json
from pgmpy.sampling.Sampling import State
from chain import Chain, ChainState
from pgmpy.models import MarkovChain
from pgmpy.factors.discrete import DiscreteFactor
from metaclasses import Singleton

import logging
# Creiamo un logger dedicato
heart_logger = logging.getLogger("HeartLogger")
heart_logger.setLevel(logging.INFO)
# File handler
fh = logging.FileHandler("server_markov.log")
fh.setLevel(logging.INFO)
# Formattazione
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
fh.setFormatter(formatter)
# Aggiungiamo handler
heart_logger.addHandler(fh)


class Heart(metaclass=Singleton):
    def __init__(self, chain: Chain = None):
        self.mapping = dict()
        self.populate(chain)
        self.states = chain.states
        self.current_state: ChainState = random.choice(self.states)

    def beat(self):
        lo_bound = self.current_state.min
        hi_bound = self.current_state.max
        beat = random.uniform(lo_bound, hi_bound)
        self.current_state = self.transition()

        # log testuale
        text = f'Stato successivo calcolato: {self.current_state.name}\nBattito {beat:.1f} bpm.'
        self.log(text)

        # --- Aggiorna current status ---
        current_status = {"current_state": self.current_state.name, "current_bpm": round(beat, 1)}
        with open("current_status.json", "w") as f:
            json.dump(current_status, f)

        # --- Aggiorna bpm history ---
        try:
            with open("bpm_history.json", "r") as f:
                bpm_history = json.load(f)
        except FileNotFoundError:
            bpm_history = []

        bpm_history.append(round(beat, 1))
        bpm_history = bpm_history[-50:]  # mantieni solo ultimi 50
        with open("bpm_history.json", "w") as f:
            json.dump(bpm_history, f)

        # --- Aggiorna distribuzione stati ---
        try:
            with open("state_counts.json", "r") as f:
                state_counts = json.load(f)
        except FileNotFoundError:
            state_counts = {state.name: 0 for state in self.states}

        state_counts[self.current_state.name] += 1
        with open("state_counts.json", "w") as f:
            json.dump(state_counts, f)

        return beat

    def transition(self):
        current_state_index = self.mapping[self.current_state.name]

        trans_dict = self.model.transition_models['beat'][current_state_index]
        total = sum(trans_dict.values())
        probs = {k: v / total for k, v in trans_dict.items()}
        self.log(f"Prob. transizione da stato {self.current_state.name}:")
        for state_index, p in probs.items():
            self.log(f"  -> Stato {self.mapping[state_index]}: {p:.4f}")

        start_point = [State(var='beat', state=current_state_index)]
        samples = list(self.model.generate_sample(start_point, 1))
        sample = samples[0][0].state
        next_state_name = self.mapping[sample]
        next_state = list(filter(lambda x: x.name == next_state_name ,self.states))[0]
        return next_state

    def populate(self, chain: Chain):
        mmodel = MarkovChain()
        # 1. Add variables (states)
        state_names = [state.name for state in chain.states]
        mmodel.add_variable("beat", len(state_names))
        # 2. Mapping
        counter = 0
        for state_name in state_names:
            self.mapping[state_name] = counter
            self.mapping[counter] = state_name
            counter += 1
        # 3. Build and set per-state transition models
        per_state_transitions = {self.mapping[name]: {} for name in state_names}
        for t in chain.transitions:
            from_index = self.mapping[t.from_state]
            to_index =  self.mapping[t.to_state]
            per_state_transitions[from_index][to_index] = t.rate
        mmodel.add_transition_model('beat', per_state_transitions)
        # 4. Store the built model
        self.model = mmodel

    def log(self, text):
        print(text)
        heart_logger.info(text)



