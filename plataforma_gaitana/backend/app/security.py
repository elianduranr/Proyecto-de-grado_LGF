import secrets
from fastapi import Header, HTTPException
from .config import DEV_MODE, TOKENS

def identity(authorization: str | None = Header(default=None)):
    if authorization:
        token = authorization.removeprefix('Bearer ')
        for valid, role in TOKENS.items():
            if secrets.compare_digest(token, valid):
                return role
        raise HTTPException(401, 'El token de acceso no es válido.')
    if DEV_MODE:
        return 'ingeniero'
    raise HTTPException(401, 'Se requiere un token de acceso.')

def can_edit(role: str):
    if role not in ('ingeniero','administrador'):
        raise HTTPException(403, 'El perfil de consulta no puede modificar pronósticos.')

