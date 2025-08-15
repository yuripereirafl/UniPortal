from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from pydantic import BaseModel
from sqlalchemy.orm import Session, sessionmaker
from app.database import engine, SessionLocal, get_db
from ..models.usuario import Usuario as UsuarioModel

router = APIRouter()
# Endpoint para listar todos os usuários
@router.get('/usuarios/')
def listar_usuarios(db: Session = Depends(get_db)):
    usuarios = db.query(UsuarioModel).all()
    return [
        {"id": u.id, "username": u.username} for u in usuarios
    ]
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

SECRET_KEY = "supersecretkey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_user(db, username: str):
    return db.query(UsuarioModel).filter(UsuarioModel.username == username).first()

def authenticate_user(db, username: str, password: str):
    user = get_user(db, username)
    if not user or not verify_password(password, user.hashed_password):
        return False
    return user

async def get_current_user(token: str = Depends(oauth2_scheme)):
    db = SessionLocal()
    credentials_exception = HTTPException(
        status_code=401,
        detail="Não autenticado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(db, username=token_data.username)
    db.close()
    if user is None:
        raise credentials_exception
    return user


from fastapi import Body

class UsuarioCreate(BaseModel):
    username: str
    password: str

@router.post('/usuarios/')
def criar_usuario(usuario: UsuarioCreate):
    db = SessionLocal()
    if db.query(UsuarioModel).filter(UsuarioModel.username == usuario.username).first():
        db.close()
        raise HTTPException(status_code=400, detail="Usuário já existe")
    hashed_password = get_password_hash(usuario.password)
    novo_usuario = UsuarioModel(username=usuario.username, hashed_password=hashed_password)
    db.add(novo_usuario)
    db.commit()
    db.close()
    return {"msg": "Usuário criado"}


# Endpoint para editar usuário

class UsuarioUpdate(BaseModel):
    username: str | None = None
    password: str | None = None

@router.put('/usuarios/{id}')
def editar_usuario(id: int, usuario_update: UsuarioUpdate):
    db = SessionLocal()
    usuario = db.query(UsuarioModel).filter(UsuarioModel.id == id).first()
    if not usuario:
        db.close()
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    if usuario_update.username:
        usuario.username = usuario_update.username
    if usuario_update.password:
        usuario.hashed_password = get_password_hash(usuario_update.password)
    db.commit()
    db.close()
    return {"msg": "Usuário atualizado"}

# Endpoint para excluir usuário
@router.delete('/usuarios/{id}')
def excluir_usuario(id: int):
    db = SessionLocal()
    usuario = db.query(UsuarioModel).filter(UsuarioModel.id == id).first()
    if not usuario:
        db.close()
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    db.delete(usuario)
    db.commit()
    db.close()
    return {"msg": "Usuário excluído"}

@router.post('/login', response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    db = SessionLocal()
    user = authenticate_user(db, form_data.username, form_data.password)
    db.close()
    if not user:
        raise HTTPException(status_code=401, detail="Usuário ou senha inválidos")
    access_token = create_access_token(data={"sub": user.username}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    return {"access_token": access_token, "token_type": "bearer"}
