# SPDX-License-Identifier: EUPL-1.2
#
# (C) Copyright 2018-2024 CSI-Piemonte

from hashlib import sha256
from binascii import a2b_base64, a2b_hex, b2a_hex
from base64 import urlsafe_b64decode
from logging import getLogger
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
from Crypto.Signature import PKCS1_v1_5
from six import b, ensure_text, ensure_binary
from beecell.crypto_util.fernet import Fernet


VAULT_MARK = "$BEEHIVE_VAULT;AES128 | "
logger = getLogger(__name__)


def check_vault(data, key):
    """
    Check if data is encrypted with fernet token and AES128.

    :param data: data to verify. If encrypted token '$BEEHIVE_VAULT;AES128 | ' is in head of data
    :param key: fernet key
    :return: decrypted key
    """
    data = ensure_binary(data)
    if data.startswith(b(VAULT_MARK)):
        if key is None:
            raise ValueError("Fernet key must be provided")
        cipher_suite = Fernet(urlsafe_b64decode(key))
        data = data.replace(b(VAULT_MARK), b(""))
        data = cipher_suite.decrypt(data)
    data = data.decode("utf-8")
    return data


def is_encrypted(data):
    """
    Check if data is encrypted with fernet token and AES128.

    :param data: data to verify. If encrypted token '$BEEHIVE_VAULT;AES128 | ' is in head of data
    :return: True if data is encrypted, False otherwise
    """
    if data.startswith(VAULT_MARK):
        return True
    return False


def generate_fernet_key():
    """
    Generate Fernet key.

    :return: fernet key
    """
    return Fernet.generate_key()


def encrypt_data(fernet_key, data):
    """
    Encrypt data using a Fernet key and a symmetric algorithm.

    :param fernet_key: Fernet key. To generate use: Fernet.generate_key()
    :param data: data to encrypt
    :return: encrypted data
    """
    cipher_suite = Fernet(urlsafe_b64decode(fernet_key))
    return VAULT_MARK + ensure_text(cipher_suite.encrypt(ensure_binary(data)))


def decrypt_data(fernet_key, data):
    """
    Decrypt data using a Fernet key and a symmetric algorithm.

    :param fernet_key: fernet key
    :param data: data to decrypt
    :return: decrypted data
    """
    data = ensure_text(data)
    if not VAULT_MARK in data:
        return data
    cipher_suite = Fernet(urlsafe_b64decode(fernet_key))
    return cipher_suite.decrypt(ensure_binary(data.removeprefix(VAULT_MARK)))


def sign_data(seckey64, data):
    """
    Sign data using public/private key signature.
    The signature algorithm used is RSA.
    The Hash algorithm used is SHA256.
    """
    # Import the key
    key = RSA.import_key(a2b_base64(seckey64))

    # Create SHA256 hash directly
    hash_data = SHA256.new(bytes(data, encoding="utf-8"))

    # Sign the hashed data
    signature = PKCS1_v1_5.new(key).sign(hash_data)

    # Return signature in hex format
    return b2a_hex(signature).decode("utf-8")


def verify_data(pubkey64, data, sign):
    """
    Verify data using public/private key signature.
    The signature algorithm used is RSA.
    The Hash algorithm used is SHA256.
    """
    # Import the public key
    key = RSA.import_key(a2b_base64(pubkey64))

    # Create SHA256 hash of the data
    hash_data = SHA256.new(bytes(data, encoding="utf-8"))

    # Verify the signature
    return PKCS1_v1_5.new(key).verify(hash_data, a2b_hex(sign))


def compute_sha256_hexdigest(data: str) -> str:
    """
    Compute SHA-256 hash of a string and return the hexadecimal digest.
    :param data: str
    :return: hexdigest
    :rtype: str
    """
    return sha256(bytes(data, encoding="utf-8")).hexdigest()
