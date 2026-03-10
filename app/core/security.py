import bcrypt
import secrets
import hashlib
import hmac

def hash_password(password: str) -> str:
    pwd_bytes = password.encode('utf-8')
    hashed = bcrypt.hashpw(pwd_bytes, bcrypt.gensalt())
    
    return hashed.decode('utf-8')

def verify_password(pwd: str, db_pwd_hash: str) -> bool:
    return bcrypt.checkpw(
        pwd.encode('utf-8'), 
        db_pwd_hash.encode('utf-8')
    )

def generate_session_tokens() -> tuple[str, str]:
    token_id = secrets.token_urlsafe(16)
    token_secret = secrets.token_urlsafe(32)
    return token_id, token_secret

def hash_session_secret(secret: str) -> str:
    return hashlib.sha256(secret.encode('utf-8')).hexdigest()

def verify_session_token(token: str, db_token_hash: str) -> bool:
    token_hash = hash_session_secret(token)
    return hmac.compare_digest(token_hash, db_token_hash)

def break_session_token(token: str | None) -> tuple[str, str] | None:
    if (token != None) and (len(token.split(".")) == 2):
        s_id, s_raw = token.split(".")
        return s_id, s_raw
    else:
        return None
