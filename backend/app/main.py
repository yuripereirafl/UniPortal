from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.funcionario import router as funcionario_router
from app.routes.sistema import router as sistema_router
from app.routes.setores import router as setores_router
from app.routes.grupo_email import router as grupo_email_router
from app.routes.grupo_pasta import router as grupo_pasta_router
from app.routes.funcionario_cargo import router as funcionario_cargo_router
from app.routes.cargo import router as cargo_router
from app.routes.cargo_opcoes import router as cargo_opcoes_router
from app.routes.quadro_colaboradores import router as quadro_colaboradores_router

from app.routes.usuario import router as usuario_router
from app.routes.relatorios import router as relatorios_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



app.include_router(funcionario_router)
app.include_router(sistema_router)
app.include_router(setores_router)
app.include_router(grupo_email_router)
app.include_router(grupo_pasta_router)
app.include_router(funcionario_cargo_router)
app.include_router(cargo_router)
app.include_router(cargo_opcoes_router)
app.include_router(quadro_colaboradores_router)

app.include_router(usuario_router)
app.include_router(relatorios_router)

@app.get('/')
def read_root():
    return {"message": "API do Sistema TI funcionando!"}
