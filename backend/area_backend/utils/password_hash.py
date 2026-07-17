from werkzeug.security import check_password_hash, generate_password_hash

# Algoritmo y parámetros de coste para el hash de contraseñas (CWE-916).
# scrypt es resistente a ataques por hardware (GPU/ASIC). Werkzeug >= 2.3 lo soporta.
# N = 2**15 (32768) y r = 8, p = 1 son valores recomendados por OWASP para scrypt.
PASSWORD_HASH_METHOD = "scrypt"
SCRYPT_N = 2 ** 15
SCRYPT_R = 8
SCRYPT_P = 1


def hash_password(password: str) -> str:
    """Genera un hash seguro de la contraseña con un coste alto y determinista."""
    return generate_password_hash(
        password,
        method=PASSWORD_HASH_METHOD,
        salt_length=16,
    )


def verify_password(hash_: str, password: str) -> bool:
    """Verifica una contraseña contra su hash."""
    return check_password_hash(hash_, password)
