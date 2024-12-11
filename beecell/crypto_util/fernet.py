# SPDX-License-Identifier: EUPL-1.2
#
# (C) Copyright 2018-2023 CSI-Piemonte

import hmac
from base64 import urlsafe_b64encode, urlsafe_b64decode
from typing import Union
from hashlib import sha256
from time import time
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes


class Fernet:
    """
    Fernet interface similar to cryptography implementation
    rewritten with cryptodome and hashlib.

    Usage:

    key_base64 = b'<some key>'
    key = urlsafe_b64decode(key_base64)  # Decode key
    fernet = Fernet(key)

    # Crypt
    token = fernet.encrypt(b'Test message')
    print("Token:", token)

    # Decrypt
    decrypted_data = fernet.decrypt(token)
    print("Decrypted data:", decrypted_data)
    """

    def __init__(self, key: Union[bytes, str, None]) -> None:
        """
        Expect a base64-encoded key of length 32 bytes.
        """
        if len(key) != 32:
            raise ValueError(
                "Fernet key must be 32 url-safe base64-encoded bytes."
            )

        self._signing_key = key[:16]  # HMAC key
        self._encryption_key = key[16:]  # AES key (128-bit)

    @staticmethod
    def generate_key():
        """
        Generate key.
        """
        return urlsafe_b64encode(get_random_bytes(32))

    def encrypt(self, data):
        """
        Encrypt.

        :param data: Data to encrypt.
        :return: Encrypted data.
        """
        # Generate a random 128-bit IV (Initialization Vector)
        iv = get_random_bytes(16)

        # Encrypt the data using AES in CBC mode with the encryption key and IV
        cipher = AES.new(self._encryption_key, AES.MODE_CBC, iv)

        # Add padding to the data
        padded_data = pad(data, AES.block_size)

        ciphertext = cipher.encrypt(padded_data)

        # Embed the current timestamp (8 bytes)
        timestamp = int(time()).to_bytes(8, byteorder="big")

        # Token format: version (1 byte) + timestamp (8 bytes) + IV (16 bytes) + ciphertext
        token = b'\x80' + timestamp + iv + ciphertext

        # HMAC (SHA256) to ensure integrity, using the signing key
        hmac_value = hmac.new(self._signing_key, token, sha256).digest()

        # Append the HMAC to the token
        token += hmac_value

        return urlsafe_b64encode(token).rstrip(b'=')

    def decrypt(self, token):
        """
        Decrypt

        :param token: Token, the minimum size is 48:
            1 byte for version + 8 byte timestamp + 16 byte IV +
            16 byte ciphertext + 32 byte HMAC.
        :return: Decrypted data.
        """
        # Decode token; add padding to be used to decode
        token = urlsafe_b64decode(token + b'==')
        token_min_size = 48
        if len(token) < token_min_size:
            raise ValueError("Invalid Token")

        # Token chunk extraction
        iv = token[9:25]
        ciphertext = token[25:-32]
        hmac_value = token[-32:]
        # version = token[0:1]
        # timestamp = token[1:9]

        # HMAC check
        expected_hmac = hmac.new(self._signing_key, token[:-32], sha256).digest()
        if not hmac.compare_digest(expected_hmac, hmac_value):
            raise ValueError('HMAC check failed')

        # Decrypt
        cipher = AES.new(self._encryption_key, AES.MODE_CBC, iv)
        padded_data = cipher.decrypt(ciphertext)

        # Remove padding
        data = unpad(padded_data, AES.block_size)
        return data
