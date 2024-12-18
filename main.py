from fastapi import FastAPI
from routers.competitions import router as items_router

app = FastAPI()

# Inclua o router
app.include_router(items_router, prefix="/api")


@app.get("/")
def read_root():
    return {"message": """
            Bem-vindo à Football API. 
            Use 
            /api/competicoes/
            /api/partidas/ 
            /api/escalacao/ 
            para acessar os dados."""}