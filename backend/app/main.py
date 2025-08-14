from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exception_handlers import RequestValidationError
from jose import JWTError, jwt
import logging

from app.routes.funcionario import router as funcionario_router
from app.routes.sistema import router as sistema_router
from app.routes.setores import router as setores_router
from app.routes.grupo_email import router as grupo_email_router
from app.routes.grupo_pasta import router as grupo_pasta_router
from app.routes.grupo import router as grupo_router
from app.routes.filial import router as filial_router

from app.routes.usuario import router as usuario_router
from app.routes.relatorios import router as relatorios_router

logging.basicConfig(level=logging.INFO)

app = FastAPI()

# Handler para mostrar erros de validação detalhados no terminal
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    print('Validation error:', exc.errors())
    print('Request body:', exc.body)
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors(), "body": exc.body},
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ou especifique os IPs do frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def verificar_permissao(request: Request, call_next):
    SECRET_KEY = "supersecretkey"
    ALGORITHM = "HS256"

    # Ignorar rotas específicas e requisições do tipo OPTIONS
    rotas_ignoradas = ["/login"]
    if request.url.path in rotas_ignoradas or request.method == "OPTIONS":
        return await call_next(request)

    if "Authorization" not in request.headers:
        logging.info("[MIDDLEWARE] Cabeçalho de autorização ausente")
        return JSONResponse(status_code=403, content={"detail": "Acesso negado"})

    token = request.headers.get("Authorization").split("Bearer ")[-1]
    logging.info(f"[MIDDLEWARE] Token recebido: {token}")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        logging.info(f"[MIDDLEWARE] Payload decodificado: {payload}")
        if not username:
            logging.info("[MIDDLEWARE] Username não encontrado no payload do token")
            raise JWTError
    except JWTError as e:
        logging.info(f"[MIDDLEWARE] Token inválido ou expirado: {str(e)}")
        return JSONResponse(status_code=403, content={"detail": "Token inválido ou expirado"})

    response = await call_next(request)
    return response

app.include_router(funcionario_router)
app.include_router(sistema_router)
app.include_router(setores_router)
app.include_router(grupo_email_router)
app.include_router(grupo_pasta_router)
app.include_router(grupo_router)
app.include_router(filial_router)

app.include_router(usuario_router)
app.include_router(relatorios_router)

@app.get('/')
def read_root():
    return {"message": "API do Sistema TI funcionando!"}

