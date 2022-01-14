# SPDX-License-Identifier: GPL-3.0-or-later
#
# (C) Copyright 2018-2019 CSI-Piemonte
# (C) Copyright 2019-2020 CSI-Piemonte
# (C) Copyright 2020-2021 CSI-Piemonte

from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from base64 import b64decode, b64encode
from six import ensure_binary, ensure_text


class RasCrypto(object):
    """Class that manage asymmetric cryptography with rsa.

    Example:

        client = RasCrypto()

        # generate new key
        private_key = client.generate_private_key()
        pem1 = client.get_private_key_pem(private_key)
        print(pem1)
        pem2 = client.get_pubblic_key_pem(private_key)
        print(pem2)

        # import private key
        private_key1 = client.import_private_key(pem1)
        # import private key
        public_key1 = client.import_public_key(pem2)

        # encrypt
        data = 'data to encrypt'
        msg = client.encrypt(public_key1, data)
        print(msg)

        # decrypt
        msg = client.decrypt(private_key1, msg)
        print(msg)
    """

    def generate_private_key(self, public_exponent=65537, key_size=2048):
        """generate new private key

        :param public_exponent:
        :param key_size:
        :return: private_key object
        """
        private_key = rsa.generate_private_key(public_exponent=public_exponent, key_size=key_size)
        return private_key

    def import_private_key(self, private_key_base64, password=None):
        """import private key

        :param private_key_base64: private key string base64 encoded
        :param password: private key password
        :return: private_key object
        """
        private_key_base64 = ensure_binary(private_key_base64)
        private_key_string = b64decode(private_key_base64)
        private_key = serialization.load_pem_private_key(private_key_string, password=password)
        return private_key

    def import_public_key(self, public_key_base64):
        """import public key

        :param public_key_base64: public key string base64 encoded
        :return: public key object
        """
        public_key_base64 = ensure_binary(public_key_base64)
        public_key_string = b64decode(public_key_base64)
        public_key = serialization.load_pem_public_key(public_key_string)
        return public_key

    def get_private_key_pem(self, private_key, password=None, base64_encode=True):
        """export private key as string

        :param private_key: private key object
        :param password: private key password [optional]
        :param base64_encode: if True encode in base64 [default=True]
        :return:
        """
        if password is None:
            pem = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption()
            )
        else:
            pem = private_key.private_bytes(
               encoding=serialization.Encoding.PEM,
               format=serialization.PrivateFormat.PKCS8,
               encryption_algorithm=serialization.BestAvailableEncryption(ensure_binary(password))
            )

        if base64_encode is True:
            pem = b64encode(pem)
        return pem

    def get_pubblic_key_pem(self, private_key, base64_encode=True):
        """export public key as string

        :param private_key: private key object
        :param base64_encode: if True encode in base64 [default=True]
        :return:
        """
        public_key = private_key.public_key()
        pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        if base64_encode is True:
            pem = b64encode(pem)
        return pem

    def encrypt(self, public_key, message, base64_encode=True):
        """Encrypt message

        :param public_key: public key object
        :param message: message to encrypt
        :param base64_encode: if True encode base64 chipher text [defualt=True]
        :return: encrypted message
        """
        ciphertext = public_key.encrypt(
            ensure_binary(message),
            padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
        )
        if base64_encode is True:
            ciphertext = b64encode(ciphertext)
        return ciphertext

    def decrypt(self, private_key, ciphertext, base64_decode=True):
        """Decrypt message

        :param private_key: private key object
        :param ciphertext: encrypted message
        :param base64_decode: if True decode base64 chipher text [defualt=True]
        :return: encrypted message
        """
        if base64_decode is True:
            ciphertext = b64decode(ciphertext)
        plaintext = private_key.decrypt(
            ciphertext,
            padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
        )
        plaintext = ensure_text(plaintext)
        return plaintext
