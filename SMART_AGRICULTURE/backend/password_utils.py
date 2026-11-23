
import os
import hashlib
import hmac
import base64

# Number of hashing iterations
ITERATIONS = 600_000


def hash_password(password):
    # Generate a random salt
    salt = os.urandom(16)

    # Convert password into a secure hash
    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        ITERATIONS
    )

    # Encode salt and hash for database storage
    salt_text = base64.b64encode(salt).decode("utf-8")
    hash_text = base64.b64encode(password_hash).decode("utf-8")

    return f"pbkdf2_sha256${ITERATIONS}${salt_text}${hash_text}"


def verify_password(password, stored_value):
    try:
        algorithm, iterations, salt_text, hash_text = stored_value.split("$")

        if algorithm != "pbkdf2_sha256":
            return False

        salt = base64.b64decode(salt_text)
        original_hash = base64.b64decode(hash_text)

        new_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            int(iterations)
        )

        return hmac.compare_digest(original_hash, new_hash)

    except (ValueError, TypeError):
        return False
