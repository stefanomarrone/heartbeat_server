import sys
from fastapi import APIRouter, FastAPI
import json
import uvicorn
from pydantic import ValidationError
from chain import Chain
from heartbeat import Heart

router = APIRouter()

@router.get("/getbeat")
def get_beat():
   heart = Heart()
   bpm = heart.beat()
   return {"beat": bpm}

if __name__ == "__main__":
   try:
      heart_configuration_filename = sys.argv[1]
      # Step 1: Read the file content
      with open(heart_configuration_filename) as f:
         data = json.load(f)
      # Step 2: Validate using Pydantic
      chain = Chain(**data)
      heart = Heart(chain)
      app = FastAPI()
      app.include_router(router)
      uvicorn.run(app, port = 4415)
   except ValidationError as exc:
      print(repr(exc.errors()[0]['type']))