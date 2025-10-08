
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from passlib.exc import UnknownHashError
import hashlib
import string
from datetime import datetime, timedelta
from pydantic import BaseModel
from sqlalchemy.orm import Session, sessionmaker, selectinload
from app.database import engine, SessionLocal, get_db
from ..models.usuario import Usuario as UsuarioModel
from ..models.permissao import Permissao as PermissaoModel
from ..models.usuarios_permissoes import usuarios_permissoes

router = APIRouter()
# Endpoint para listar todos os usuários (com setores carregados)
@router.get('/usuarios/')
def listar_usuarios(db: Session = Depends(get_db)):
    usuarios = db.query(UsuarioModel).options(selectinload(UsuarioModel.setores)).all()
    print("[DEBUG] Usuários carregados:")
    for u in usuarios:
        print(f"Usuário: {u.id} - {u.username} | Setores: {[{'id': s.id, 'nome': s.nome} for s in u.setores]}")
    result = []
    for u in usuarios:
        # carregar permissões vinculadas via tabela usuarios_permissoes (diretas)
        permissoes_direct = db.query(PermissaoModel).join(usuarios_permissoes).filter(usuarios_permissoes.c.usuario_id == u.id).all()
        # carregar permissões via grupos do usuário
        from ..models.usuario_grupo import usuario_grupo
        # nome correto da tabela de associação é 'grupo_permissao' (definida em grupo_permissao.py)
        from ..models.grupo_permissao import grupo_permissao
        permissoes_via_grupo = db.query(PermissaoModel).join(grupo_permissao).join(usuario_grupo, grupo_permissao.c.grupo_id == usuario_grupo.c.grupo_id).filter(usuario_grupo.c.usuario_id == u.id).all()
        # deduplicar
        permissoes_map = {p.id: p for p in (permissoes_direct + permissoes_via_grupo)}
        permissoes = list(permissoes_map.values())

        def normalize_code(s):
            if s is None:
                return ''
            return ''.join(ch for ch in str(s).strip().lower().replace(' ', '_') if (ch.isalnum() or ch == '_'))

        permissoes_out = []
        for p in permissoes:
            permissoes_out.append({
                "id": p.id,
                "codigo": p.codigo,
                "descricao": p.descricao,
                "codigo_normalized": normalize_code(p.codigo or p.descricao)
            })

        result.append({
            "id": u.id,
            "username": u.username,
            "setores": [{"id": s.id, "nome": s.nome, "descricao": s.descricao} for s in u.setores],
            "permissoes": permissoes_out
        })
    return result
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

SECRET_KEY = "supersecretkey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

def verify_password(plain_password, hashed_password):
    """Verifica a senha com suporte a formatos legados.

    Retorna uma tupla (is_valid: bool, needs_rehash: bool).
    needs_rehash é True quando o hash era legível por fallback (MD5/SHA1/texto)
    e deveria ser atualizado para o esquema atual do pwd_context.
    """
    try:
        valid = pwd_context.verify(plain_password, hashed_password)
        # se for válido, verificar se o hash precisa de atualização (parâmetros antigos)
        try:
            needs = pwd_context.needs_update(hashed_password)
        except Exception:
            needs = False
        return valid, bool(needs)
    except UnknownHashError:
        # tenta MD5 (32 hex)
        try:
            if hashed_password and len(hashed_password) == 32 and all(c in string.hexdigits for c in hashed_password):
                matched = hashlib.md5(plain_password.encode()).hexdigest() == hashed_password.lower()
                return matched, matched
            # tenta SHA1 (40 hex)
            if hashed_password and len(hashed_password) == 40 and all(c in string.hexdigits for c in hashed_password):
                matched = hashlib.sha1(plain_password.encode()).hexdigest() == hashed_password.lower()
                return matched, matched
        except Exception:
            pass
        # como último recurso, compara texto puro (apenas para migração/dev)
        matched = plain_password == hashed_password
        return matched, matched

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
    if not user:
        return None, False
    is_valid, needs_rehash = verify_password(password, user.hashed_password)
    if not is_valid:
        return None, False
    return user, needs_rehash

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


@router.get('/me')
def read_current_user(current_user: UsuarioModel = Depends(get_current_user)):
    """Retorna os dados do usuário autenticado, incluindo permissões, setores e funcionário associado."""
    db = SessionLocal()
    # carregar permissoes via tabela usuarios_permissoes
    from ..models.permissao import Permissao as PermissaoModel
    from ..models.usuarios_permissoes import usuarios_permissoes
    # permissões diretas vinculadas ao usuário
    permissoes_direct = db.query(PermissaoModel).join(usuarios_permissoes).filter(usuarios_permissoes.c.usuario_id == current_user.id).all()
    # permissões vindas via grupos do usuário
    from ..models.usuario_grupo import usuario_grupo
    from ..models.grupo_permissao import grupo_permissao
    permissoes_via_grupo = db.query(PermissaoModel).join(grupo_permissao).join(usuario_grupo, grupo_permissao.c.grupo_id == usuario_grupo.c.grupo_id).filter(usuario_grupo.c.usuario_id == current_user.id).all()
    # unir e deduplicar
    permissoes_map = {p.id: p for p in (permissoes_direct + permissoes_via_grupo)}
    permissoes = list(permissoes_map.values())
    # recarregar usuário com setores via uma sessão ativa para evitar DetachedInstanceError
    from sqlalchemy.orm import selectinload
    user_with_setores = db.query(UsuarioModel).options(selectinload(UsuarioModel.setores)).filter(UsuarioModel.id == current_user.id).first()
    if user_with_setores:
        setores = [{"id": s.id, "nome": s.nome, "descricao": s.descricao} for s in user_with_setores.setores]
    else:
        setores = []
    
    # Carregar dados do funcionário associado ao usuário
    funcionario_data = None
    if current_user.id_funcionario:
        from ..models.funcionario import Funcionario
        funcionario = db.query(Funcionario).filter(Funcionario.id == current_user.id_funcionario).first()
        if funcionario:
            funcionario_data = {
                "id": funcionario.id,
                "nome": funcionario.nome,
                "sobrenome": funcionario.sobrenome,
                "cpf": funcionario.cpf,
                "email": funcionario.email,
                "equipe": funcionario.equipe
            }
    
    # DEBUG: mostrar no log do servidor as permissões retornadas para este usuário
    try:
        print(f"[DEBUG /me] usuario={current_user.username} funcionario_id={current_user.id_funcionario} permissoes={[{'id': p.id, 'codigo': p.codigo, 'descricao': p.descricao} for p in permissoes]}")
    except Exception:
        pass
    db.close()
    # Normalizar código para facilitar uso no frontend
    def normalize_code(s):
        if s is None:
            return ''
        return ''.join(ch for ch in str(s).strip().lower().replace(' ', '_') if (ch.isalnum() or ch == '_'))

    permissoes_out = []
    for p in permissoes:
        permissoes_out.append({
            "id": p.id,
            "codigo": p.codigo,
            "descricao": p.descricao,
            "codigo_normalized": normalize_code(p.codigo or p.descricao)
        })

    return {
        "id": current_user.id,
        "username": current_user.username,
        "id_funcionario": current_user.id_funcionario,
        "setores": setores,
        "permissoes": permissoes_out,
        "funcionario": funcionario_data
    }


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
    setores_ids: list[int] | None = None

@router.put('/usuarios/{id}')
def editar_usuario(id: int, usuario_update: UsuarioUpdate):
    db = SessionLocal()
    try:
        usuario = db.query(UsuarioModel).filter(UsuarioModel.id == id).first()
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
        
        if usuario_update.username:
            usuario.username = usuario_update.username
        if usuario_update.password:
            usuario.hashed_password = get_password_hash(usuario_update.password)
        
        if usuario_update.setores_ids is not None:
            # Primeiro, remove associações antigas de setores do usuário
            from ..models.usuario import usuario_setor
            db.execute(usuario_setor.delete().where(usuario_setor.c.usuario_id == id))
            
            # Adiciona novas associações de setores
            for setor_id in usuario_update.setores_ids:
                db.execute(usuario_setor.insert().values(usuario_id=id, setor_id=setor_id))
            
            # Atualiza setores do funcionário vinculado se existir
            if usuario.id_funcionario:
                from ..models.funcionario import funcionario_setor
                # Remove associações antigas do funcionário
                db.execute(funcionario_setor.delete().where(funcionario_setor.c.funcionario_id == usuario.id_funcionario))
                # Adiciona novas associações
                for setor_id in usuario_update.setores_ids:
                    db.execute(funcionario_setor.insert().values(funcionario_id=usuario.id_funcionario, setor_id=setor_id))
        
        db.commit()
        return {"msg": "Usuário e funcionário atualizados"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao editar usuário: {str(e)}")
    finally:
        db.close()

# Endpoint para excluir usuário
@router.delete('/usuarios/{id}')
def excluir_usuario(id: int):
    db = SessionLocal()
    try:
        usuario = db.query(UsuarioModel).filter(UsuarioModel.id == id).first()
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
        
        # Primeiro, remover associações de permissões diretas
        db.execute(usuarios_permissoes.delete().where(usuarios_permissoes.c.usuario_id == id))
        
        # Remover associações de grupos
        from ..models.usuario_grupo import usuario_grupo
        db.execute(usuario_grupo.delete().where(usuario_grupo.c.usuario_id == id))
        
        # Agora excluir o usuário
        db.delete(usuario)
        db.commit()
        return {"msg": "Usuário excluído"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao excluir usuário: {str(e)}")
    finally:
        db.close()


@router.put('/usuarios/{id}/permissoes')
def atualizar_permissoes_usuario(id: int, payload: dict = Body(...)):
    """Atualiza as permissões associadas a um usuário.
    Espera payload = {"permissoes_ids": [1,2,3]} (lista pode estar vazia).
    """
    permissoes_ids = payload.get('permissoes_ids', [])
    db = SessionLocal()
    usuario = db.query(UsuarioModel).filter(UsuarioModel.id == id).first()
    if not usuario:
        db.close()
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    # remove associações existentes de permissões diretas
    db.execute(usuarios_permissoes.delete().where(usuarios_permissoes.c.usuario_id == id))
    # também remover associações de grupo para garantir que as permissões do usuário
    # fiquem exatamente as informadas (sem herdar permissões via grupo).
    # Isso implementa a regra solicitada: quando definimos explicitamente as
    # permissões de um usuário, ele não deverá herdar permissões de grupos.
    try:
        from ..models.usuario_grupo import usuario_grupo
        db.execute(usuario_grupo.delete().where(usuario_grupo.c.usuario_id == id))
    except Exception:
        # se a tabela/modelo não existir por algum motivo, ignoramos silenciosamente
        # (não queremos que uma falha aqui impeça a atualização das permissões).
        db.rollback()
    # inserir novas associações
    for pid in permissoes_ids:
        db.execute(usuarios_permissoes.insert().values(usuario_id=id, permissao_id=pid))
    db.commit()
    # carregar permissões atualizadas para retorno
    permissoes = db.query(PermissaoModel).join(usuarios_permissoes).filter(usuarios_permissoes.c.usuario_id == id).all()
    db.close()
    return {"msg": "Permissões atualizadas", "permissoes": [{"id": p.id, "codigo": p.codigo, "descricao": p.descricao} for p in permissoes]}

@router.post('/login', response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    db = SessionLocal()
    user, needs_rehash = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        db.close()
        raise HTTPException(status_code=401, detail="Usuário ou senha inválidos")
    # Se senha veio de formato legado, re-hash e atualiza no banco
    if needs_rehash:
        try:
            user.hashed_password = get_password_hash(form_data.password)
            db.add(user)
            db.commit()
        except Exception:
            db.rollback()
    access_token = create_access_token(data={"sub": user.username}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    db.close()
    return {"access_token": access_token, "token_type": "bearer"}
