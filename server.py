from fastapi import APIRouter, FastAPI
import uvicorn
import random
router = APIRouter()

from fastapi import FastAPI
import uvicorn
import random
from collections import defaultdict

# from pgmpy.models import MarkovChain

app = FastAPI()

# Stati Markoviani
states = ["Q1", "Q2", "Q3", "Q4"]
state_counts = defaultdict(lambda: defaultdict(int))
last_state = {"value": None}


# Classificazione dei BPM
def classify_bpm(bpm):
   if bpm < 60:
      return "Q1"
   elif 60 <= bpm < 100:
      return "Q2"
   elif 100 <= bpm < 120:
      return "Q3"
   else:
      return "Q4"


# Range dei BPM per ciascuno stato
bpm_ranges = {
   "Q1": (40, 59),
   "Q2": (60, 99),
   "Q3": (100, 119),
   "Q4": (120, 150)
}


# Endpoint per ottenere un nuovo beat (BPM)
@app.get("/getbeat")
def get_beat():
   if last_state["value"] is None:
      # Prima chiamata: BPM completamente casuale
      bpm = random.randint(50, 140)
      current_state = classify_bpm(bpm)

   else:
      # Chiamate successive: generazione pesata secondo catena di Markov
      transition_matrix = get_transition_matrix()
      current_state = last_state["value"]
      probs = transition_matrix[current_state]
      weights = [probs[s] for s in states]  # lista di probabilità per ogni stato

      # Se tutti i pesi sono 0, scegli uno stato a caso
      if sum(weights) == 0:
         next_state = random.choice(states)
      else:
         next_state = random.choices(states, weights=weights, k=1)[0]

      # Generazione BPM nel range dello stato selezionato
      bpm = random.randint(*bpm_ranges[next_state])
      current_state = next_state

      # Registrazione transizione
      state_counts[last_state["value"]][current_state] += 1

   # Aggiorna stato precedente
   last_state["value"] = current_state

   return {"beat": bpm, "state": current_state}


# Creazione della matrice di transizione
def get_transition_matrix():
   matrix = {}
   for from_state in states:
      total = sum(state_counts[from_state].values())
      matrix[from_state] = {}
      for to_state in states:
         count = state_counts[from_state][to_state]
         matrix[from_state][to_state] = (count + 1) / (total + len(states))
         # count / total if total > 0 else 0.0
   return matrix


# Endpoint per visualizzare la matrice di transizione
@app.get("/matrix")
def show_matrix():
   matrix = get_transition_matrix()
   return matrix


# Calcolo delle probabilità di transizione
@app.get("/get_next_state_prob")
def get_next_state_prob():
   current_state = last_state["value"]
   if not current_state:
      return {"error": "Nessun stato iniziale rilevato"}

   transition_matrix = get_transition_matrix()

   # Otteniamo le probabilità dalla matrice
   probs = transition_matrix[current_state]

   # Convertiamo in percentuale
   next_state_probs_percent = {
      state: f"{round(prob * 100, 2)}%" for state, prob in probs.items()
   }

   return {
      "current_state": current_state,
      "next_state_probs": next_state_probs_percent
   }


if __name__ == "__main__":
   app = FastAPI()
   app.include_router(router)
   uvicorn.run(app, port = 4415)