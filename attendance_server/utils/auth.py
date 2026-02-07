import jwt
from config import SECRET_KEY, ALGORITHM

def verify_jwt(token: str):
    """Verify JWT token and return payload"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload, None
    except jwt.ExpiredSignatureError:
        return None, "Token expired"
    except jwt.InvalidSignatureError:
        return None, "Invalid token signature"
    except jwt.InvalidTokenError:
        return None, "Invalid token"