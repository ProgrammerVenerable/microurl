import string
import secrets

def generate_short_code(length: int = 6) -> str:
    characters = string.ascii_letters + string.digits

    code = ""
    for i in range(length):
        code += code.join(secrets.choice(characters))
    return code