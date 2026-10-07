import base64
import hashlib
import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def create_key(password):
    """
    Convert a shared password into a 32-byte AES-256 key.
    """
    return hashlib.sha256(password.encode("utf-8")).digest()


def encrypt_message(message, key):
    """
    Encrypt a message using AES-256-GCM.

    A new random 12-byte nonce is generated for every message.
    """
    nonce = os.urandom(12)

    aes = AESGCM(key)
    encrypted = aes.encrypt(
        nonce,
        message.encode("utf-8"),
        None
    )

    # Send nonce together with ciphertext + authentication tag.
    combined = nonce + encrypted

    return base64.b64encode(combined).decode("utf-8")


def decrypt_message(encrypted_message, key):
    """
    Decrypt an AES-256-GCM encrypted message.
    """
    try:
        combined = base64.b64decode(encrypted_message.encode("utf-8"))

        nonce = combined[:12]
        ciphertext = combined[12:]

        aes = AESGCM(key)

        decrypted = aes.decrypt(
            nonce,
            ciphertext,
            None
        )

        return decrypted.decode("utf-8")

    except Exception:
        return None