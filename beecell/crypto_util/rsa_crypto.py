# SPDX-License-Identifier: EUPL-1.2
#
# (C) Copyright 2018-2023 CSI-Piemonte

from hashlib import sha256
from base64 import b64decode, b64encode
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA


class RasCrypto:
    """
    Class that manages asymmetric cryptography with RSA using hashlib for SHA256.
    """

    def generate_private_key(self, public_exponent=65537, key_size=2048):
        """
        Generate new private key.
        """
        return  RSA.generate(key_size, e=public_exponent)

    def import_private_key(self, private_key_base64, password=None):
        """
        Import private key.
        """
        private_key_bytes = b64decode(private_key_base64)
        return RSA.import_key(private_key_bytes, passphrase=password)

    def import_public_key(self, public_key_base64):
        """
        Import public key.
        """
        public_key_bytes = b64decode(public_key_base64)
        return RSA.import_key(public_key_bytes)

    def get_private_key_pem(self, private_key, password=None, base64_encode=True):
        """
        Export private key as string.
        """
        if password is not None:
            pem = private_key.export_key(format='PEM', passphrase=password, pkcs=8)
        else:
            pem = private_key.export_key(format='PEM')
        if not base64_encode:
            return pem
        return b64encode(pem)

    def get_public_key_pem(self, private_key, base64_encode=True):
        """
        Export public key as string.
        """
        pem = private_key.publickey().export_key(format='PEM')
        if not base64_encode:
            return pem
        return b64encode(pem)

    def encrypt(self, public_key, message, base64_encode=True):
        """
        Encrypt message.
        """
        # Create a PKCS1_OAEP cipher using hashlib's sha256
        cipher = PKCS1_OAEP.new(public_key, hashAlgo=sha256)
        ciphertext = cipher.encrypt(message.encode('utf-8'))

        if not base64_encode:
            return ciphertext
        return b64encode(ciphertext)

    def decrypt(self, private_key, ciphertext, base64_decode=True):
        """
        Decrypt message.
        """
        if base64_decode:
            ciphertext = b64decode(ciphertext)
        # Create a PKCS1_OAEP cipher using hashlib's sha256
        cipher = PKCS1_OAEP.new(private_key, hashAlgo=sha256)
        return cipher.decrypt(ciphertext).decode('uft-8')
