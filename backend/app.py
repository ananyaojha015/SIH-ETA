from fastapi import FastAPI
from routes import train, simulation, reports

app = FastAPI(title="SIH ETA Backend")

app.include_router(train.router)
app.include_router(simulation.router)
app.include_router(reports.router)

@app.get("/health")
def health_check():
    return {"status": "ok"}