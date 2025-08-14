from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.grupos import Grupo
from app.models.permissoes import Permissao
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
    grupos = db.query(Grupo).join(usuario_grupo).filter(usuario_grupo.c.usuario_id == user.id).all()
    for grupo in grupos:
        # Join usando o relacionamento ORM, não a lista de objetos
        permissoes = db.query(Permissao).join(Permissao.grupos).filter(Grupo.id == grupo.id, Permissao.codigo == permission_code).all()
        if permissoes:
            return True
    return False
