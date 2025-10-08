from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.usuario import Usuario as User
from app.models.grupos import Grupo
from app.models.permissao import Permissao
from app.models.usuario_grupo import usuario_grupo
from jose import jwt, JWTError
from app.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)) -> User:
    import logging
    try:
        logging.info(f"[get_current_user] Token recebido: {token}")
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        logging.info(f"[get_current_user] Payload decodificado: {payload}")
        username: str = payload.get("sub")
        if username is None:
            logging.info("[get_current_user] Username não encontrado no payload do token")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido ou expirado",
                headers={"WWW-Authenticate": "Bearer"},
            )
        user = db.query(User).filter(User.username == username).first()
        if user is None:
            logging.info(f"[get_current_user] Usuário '{username}' não encontrado no banco de dados")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuário não encontrado",
                headers={"WWW-Authenticate": "Bearer"},
            )
        logging.info(f"[get_current_user] Usuário autenticado: {user.username}")
        return user
    except JWTError as e:
        logging.info(f"[get_current_user] Token inválido ou expirado: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )

def has_permission(user: User, permission_code: str, db: Session) -> bool:
    def normalize_code(s: str):
        if s is None:
            return ''
        return ''.join(ch for ch in str(s).strip().lower().replace(' ', '_') if (ch.isalnum() or ch == '_'))

    target = normalize_code(permission_code)

    # Permissões diretas do usuário
    from app.models.usuarios_permissoes import usuarios_permissoes
    direct = db.query(Permissao).join(usuarios_permissoes).filter(usuarios_permissoes.c.usuario_id == user.id).all()
    for p in direct:
        if normalize_code(p.codigo or p.descricao) == target:
            return True

    # Permissões via grupos
    grupos = db.query(Grupo).join(usuario_grupo).filter(usuario_grupo.c.usuario_id == user.id).all()
    for grupo in grupos:
        permissoes = db.query(Permissao).join(Permissao.grupos).filter(Grupo.id == grupo.id).all()
        for p in permissoes:
            if normalize_code(p.codigo or p.descricao) == target:
                return True

    return False


def permission_required(permission_code: str):
    """Factory que retorna uma dependência FastAPI para exigir uma permissão.

    Uso em rotas:
      @router.get('/algo', dependencies=[Depends(permission_required('Meta Colaborador'))])
    """
    def _require_permission(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
        if not has_permission(user, permission_code, db):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Usuário não tem permissão: {permission_code}"
            )
        return True

    return _require_permission
