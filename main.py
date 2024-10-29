from fastapi import FastAPI, HTTPException

from registrability.api import FeatureParams
from models import RegistrabilityRequest

app = FastAPI()
feature_params = FeatureParams()





@app.post("/registrability/")
async def registrability_endpoint(request: RegistrabilityRequest):
    try:
        result = feature_params.registrability_params(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app,host="127.0.0.1",port=8000)