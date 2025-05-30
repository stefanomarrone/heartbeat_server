from fastapi import APIRouter, FastAPI
from collections import defaultdict
import uvicorn
import random

router = APIRouter()



# Range dei BPM per ciascuno stato
bpm_ranges = {
}


# Endpoint per ottenere un nuovo beat (BPM)
@app.get("/getbeat")
def get_beat():
   bpm = 0
   return {"beat": bpm}




if __name__ == "__main__":
   heart_configuration_filename = sys.argv[0]
   app = FastAPI()
   app.include_router(router)
   uvicorn.run(app, port = 4415)