# routes/password_reset.py
from services.password_reset import password_reset

def auth_password_reset():
    return password_reset()