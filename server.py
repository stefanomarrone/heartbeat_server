from fastapi import APIRouter, FastAPI
import uvicorn
import random
router = APIRouter()


@router.get("/getbeat")
def beat():
   current_bpm = random.randrange(50, 141)  #BPM tra 50 e 140 battiti
   #il secondo valore escluso, quindi 141 per includere 140
   return {'beat': current_bpm}

app = FastAPI()
app.include_router(router)
uvicorn.run(app, port = 4415)