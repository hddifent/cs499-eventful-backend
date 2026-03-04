import bcrypt

def hash_password(password: str) -> str:
    pwd_bytes = password.encode('utf-8')
    hashed = bcrypt.hashpw(pwd_bytes, bcrypt.gensalt())
    
    return hashed.decode('utf-8')

def verify_password(pwd: str, db_pwd_hash: str) -> bool:
    return bcrypt.checkpw(
        pwd.encode('utf-8'), 
        db_pwd_hash.encode('utf-8')
    )