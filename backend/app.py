from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import train, simulation, reports

app = FastAPI(title="SIH ETA Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Day 2/demo scope: allow all origins for simplicity
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(train.router)
app.include_router(simulation.router)
app.include_router(reports.router)

@app.get("/health")
def health_check():
    return {"status": "ok"}