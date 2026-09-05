from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import health, mandi, diagnostics, forecast, sale_window

app = FastAPI(title="AgriEdge API")

# Configure CORS
origins = [
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(mandi.router)
app.include_router(diagnostics.router)
app.include_router(forecast.router)
app.include_router(sale_window.router)
