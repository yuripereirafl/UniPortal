
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from pydantic import BaseModel
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.sql import text
from app.database import engine, SessionLocal, get_db
from ..models.usuario import Usuario as UsuarioModel
from app.models.usuarios_permissoes import usuarios_permissoes
from app.models.grupos import Grupo

router = APIRouter()

# Configurações de autenticação
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

SECRET_KEY = "supersecretkey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["sha512_crypt", "sha256_crypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

def verify_password(plain_password, hashsenha):
    return pwd_context.verify(plain_password, hashsenha)

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
    if not user or not verify_password(password, user.hashsenha):
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

# Endpoint para listar todos os usuários
@router.get('/usuarios/')
def listar_usuarios(
    db: Session = Depends(get_db),
    current_user: UsuarioModel = Depends(get_current_user)
):
    usuarios = db.query(UsuarioModel).all()
    resultado = []
    for usuario in usuarios:
        grupos = db.execute(
            text("""
            SELECT g.id, g.nome
            FROM grupos g
            JOIN usuario_grupo ug ON g.id = ug.grupo_id
            WHERE ug.usuario_id = :usuario_id
            """),
            {"usuario_id": usuario.id}
        ).fetchall()

        unidades = db.execute(
            text("""
            SELECT f.id, f.unidade
            FROM usuario_unidade uu
            JOIN filial f ON uu.filial_id = f.id
            WHERE uu.usuario_id = :usuario_id
            """),
            {"usuario_id": usuario.id}
        ).fetchall()

        resultado.append({
            "id": usuario.id,
            "username": usuario.username,
            "grupos": [{"id": g.id, "nome": g.nome} for g in grupos],
            "unidades": [{"id": u.id, "unidade": u.unidade} for u in unidades]
        })
    return resultado
# Endpoint para vincular ou alterar unidade do usuário
@router.put('/usuarios/{id}/unidade')
def vincular_unidade_usuario(id: int, unidade_id: int = Query(...), db: Session = Depends(get_db)):
    usuario = db.query(UsuarioModel).filter(UsuarioModel.id == id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    # Remove vínculos anteriores
    db.execute(
        text("""
        DELETE FROM usuario_unidade WHERE usuario_id = :usuario_id
        """),
        {"usuario_id": id}
    )
    # Adiciona novo vínculo
    db.execute(
        text("""
        INSERT INTO usuario_unidade (usuario_id, filial_id)
        VALUES (:usuario_id, :filial_id)
        """),
        {"usuario_id": id, "filial_id": unidade_id}
    )
    db.commit()
    return {"msg": "Unidade vinculada ao usuário com sucesso"}

# Classes de dados para criação e edição de usuários


class UsuarioCreate(BaseModel):
    nome: str
    email: str
    grupos_ids: list[int] = []
    unidades_ids: list[int] = []


@router.post('/usuarios/')
def criar_usuario(
    usuario_data: UsuarioCreate,
    db: Session = Depends(get_db),
    current_user: UsuarioModel = Depends(get_current_user)
):
    # Cria o usuário
    novo_usuario = UsuarioModel(
        username=usuario_data.nome, 
        hashsenha=pwd_context.hash(usuario_data.email)
    )
    db.add(novo_usuario)
    db.commit()
    db.refresh(novo_usuario)

    # Vincula grupos se informado
    for grupo_id in usuario_data.grupos_ids:
        grupo = db.query(Grupo).filter(Grupo.id == grupo_id).first()
        if grupo:
            db.execute(
                text("""
                INSERT INTO usuario_grupo (usuario_id, grupo_id)
                VALUES (:usuario_id, :grupo_id)
                """),
                {"usuario_id": novo_usuario.id, "grupo_id": grupo.id}
            )
            db.commit()

    # Vincula unidades (filiais) se informado
    for unidade_id in usuario_data.unidades_ids:
        db.execute(
            text("""
            INSERT INTO usuario_unidade (usuario_id, filial_id)
            VALUES (:usuario_id, :filial_id)
            """),
            {"usuario_id": novo_usuario.id, "filial_id": unidade_id}
        )
    db.commit()

    return {"id": novo_usuario.id, "username": novo_usuario.username}


# Endpoint para editar usuário

class UsuarioUpdate(BaseModel):
    nome: str | None = None
    email: str | None = None
    password: str | None = None
    grupos_ids: list[int] | None = None
    unidades_ids: list[int] | None = None

@router.put('/usuarios/{id}')
def editar_usuario(
    id: int, 
    usuario_update: UsuarioUpdate,
    db: Session = Depends(get_db),
    current_user: UsuarioModel = Depends(get_current_user)
):
    usuario = db.query(UsuarioModel).filter(UsuarioModel.id == id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    # Atualiza dados básicos do usuário
    if usuario_update.nome:
        usuario.username = usuario_update.nome
    if usuario_update.password:
        usuario.hashsenha = get_password_hash(usuario_update.password)
    
    # Atualiza grupos se fornecido
    if usuario_update.grupos_ids is not None:
        # Remove todos os grupos existentes
        db.execute(
            text("DELETE FROM usuario_grupo WHERE usuario_id = :usuario_id"),
            {"usuario_id": id}
        )
        # Adiciona novos grupos
        for grupo_id in usuario_update.grupos_ids:
            grupo = db.query(Grupo).filter(Grupo.id == grupo_id).first()
            if grupo:
                db.execute(
                    text("""
                    INSERT INTO usuario_grupo (usuario_id, grupo_id)
                    VALUES (:usuario_id, :grupo_id)
                    """),
                    {"usuario_id": id, "grupo_id": grupo_id}
                )
    
    # Atualiza unidades se fornecido
    if usuario_update.unidades_ids is not None:
        # Remove todas as unidades existentes
        db.execute(
            text("DELETE FROM usuario_unidade WHERE usuario_id = :usuario_id"),
            {"usuario_id": id}
        )
        # Adiciona novas unidades
        for unidade_id in usuario_update.unidades_ids:
            db.execute(
                text("""
                INSERT INTO usuario_unidade (usuario_id, filial_id)
                VALUES (:usuario_id, :filial_id)
                """),
                {"usuario_id": id, "filial_id": unidade_id}
            )
    
    db.commit()
    return {"msg": "Usuário atualizado com sucesso"}


# Endpoint para excluir usuário
@router.delete('/usuarios/{id}')
def excluir_usuario(
    id: int,
    db: Session = Depends(get_db),
    current_user: UsuarioModel = Depends(get_current_user)
):
    usuario = db.query(UsuarioModel).filter(UsuarioModel.id == id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    # Remove vínculos com grupos
    db.execute(
        text("DELETE FROM usuario_grupo WHERE usuario_id = :usuario_id"),
        {"usuario_id": id}
    )
    
    # Remove vínculos com unidades
    db.execute(
        text("DELETE FROM usuario_unidade WHERE usuario_id = :usuario_id"),
        {"usuario_id": id}
    )
    
    # Remove o usuário
    db.delete(usuario)
    db.commit()
    return {"msg": "Usuário excluído com sucesso"}

# Endpoint para vincular ou alterar unidades do usuário
@router.put('/usuarios/{id}/unidades')
def vincular_unidades_usuario(
    id: int, 
    unidades_ids: list[int] = Body(...), 
    db: Session = Depends(get_db),
    current_user: UsuarioModel = Depends(get_current_user)
):
    usuario = db.query(UsuarioModel).filter(UsuarioModel.id == id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    # Remove vínculos anteriores
    db.execute(
        text("""
        DELETE FROM usuario_unidade WHERE usuario_id = :usuario_id
        """),
        {"usuario_id": id}
    )
    # Adiciona novos vínculos
    for unidade_id in unidades_ids:
        db.execute(
            text("""
            INSERT INTO usuario_unidade (usuario_id, filial_id)
            VALUES (:usuario_id, :filial_id)
            """),
            {"usuario_id": id, "filial_id": unidade_id}
        )
    db.commit()
    return {"msg": "Unidades vinculadas ao usuário com sucesso"}

@router.post('/login', response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    db = SessionLocal()
    user = authenticate_user(db, form_data.username, form_data.password)
    db.close()
    if not user:
        raise HTTPException(status_code=401, detail="Usuário ou senha inválidos")
    access_token = create_access_token(data={"sub": user.username}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    return {"access_token": access_token, "token_type": "bearer"}

@router.get('/usuarios/{id}/grupos')
def listar_grupos_usuario(id: int):
    db = SessionLocal()
    usuario = db.query(UsuarioModel).filter(UsuarioModel.id == id).first()
    if not usuario:
        db.close()
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    grupos = db.execute(
        """
        SELECT g.id, g.name, g.descricao
        FROM grupos g
        JOIN usuarios_permissoes up ON g.id = up.permissao_id
        WHERE up.usuario_id = :usuario_id
        """,
        {"usuario_id": id}
    ).fetchall()

    db.close()
    return [{"id": g.id, "name": g.name, "descricao": g.descricao} for g in grupos]

@router.put('/usuarios/{id}/grupos')
def editar_grupos_usuario(id: int, grupo_ids: list[int]):
    db = SessionLocal()
    usuario = db.query(UsuarioModel).filter(UsuarioModel.id == id).first()
    if not usuario:
        db.close()
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    # Remover associações existentes
    db.execute(
        """
        DELETE FROM rh_homologacao.usuarios_permissoes
        WHERE usuario_id = :usuario_id
        """,
        {"usuario_id": id}
    )

    # Adicionar novas associações
    for grupo_id in grupo_ids:
        db.execute(
            """
            INSERT INTO rh_homologacao.usuarios_permissoes (usuario_id, permissao_id)
            VALUES (:usuario_id, :grupo_id)
            """,
            {"usuario_id": id, "grupo_id": grupo_id}
        )

    db.commit()
    db.close()
    return {"msg": "Grupos atualizados com sucesso"}

@router.get("/verificar-permissao")
def verificar_permissao():
    """Endpoint para verificar se a aplicação está funcionando"""
    return {"status": "ok", "message": "Aplicação funcionando"}
