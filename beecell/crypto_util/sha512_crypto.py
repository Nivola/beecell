# SPDX-License-Identifier: EUPL-1.2
#
# (C) Copyright 2018-2023 CSI-Piemonte

import hashlib
import typing
import secrets

# Constants
ROUNDS_DEFAULT = 5000
ALPHABET = [ord(c) for c in "./0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"]

# Predefined permutation for base64 encoding
PERMUTATION = [
    [0, 21, 42],
    [22, 43, 1],
    [44, 2, 23],
    [3, 24, 45],
    [25, 46, 4],
    [47, 5, 26],
    [6, 27, 48],
    [28, 49, 7],
    [50, 8, 29],
    [9, 30, 51],
    [31, 52, 10],
    [53, 11, 32],
    [12, 33, 54],
    [34, 55, 13],
    [56, 14, 35],
    [15, 36, 57],
    [37, 58, 16],
    [59, 17, 38],
    [18, 39, 60],
    [40, 61, 19],
    [62, 20, 41],
    [-1, -1, 63],
]


def custom_b64_encode(data: bytes) -> str:
    """Custom base64 encoding for crypt."""
    result = bytearray(4 * len(PERMUTATION))
    for i, group in enumerate(PERMUTATION):
        # Access data values based on the current permutation
        bits = sum((data[j] if j != -1 else 0) << (8 * (2 - idx)) for idx, j in enumerate(group))
        result[i * 4] = ALPHABET[bits & 63]
        result[i * 4 + 1] = ALPHABET[(bits >> 6) & 63]
        result[i * 4 + 2] = ALPHABET[(bits >> 12) & 63]
        result[i * 4 + 3] = ALPHABET[(bits >> 18) & 63]
    return bytes(result).decode("ascii")[:-2]


def repeat_to_length(data: bytes, length: int) -> bytes:
    """Repeat byte string to the specified length."""
    return (data * (length // len(data))) + data[: length % len(data)]


def digest(data: bytes) -> bytes:
    """Generate SHA512 digest."""
    return hashlib.sha512(data).digest()


def sha512_crypt(
    password: typing.Union[bytes, str], salt: typing.Union[bytes, str], rounds: int = ROUNDS_DEFAULT
) -> str:
    """Custom implementation of SHA512-crypt."""
    # Ensure password and salt are byte-encoded
    if isinstance(password, str):
        password = password.encode("utf-8")
    if salt is None:
        salt = custom_b64_encode(secrets.token_bytes(64))[:16].encode("ascii")
    elif isinstance(salt, str):
        salt = salt.encode("utf-8")
    salt = salt[:16]

    # Initial hash calculations (A and B)
    b = digest(password + salt + password)
    a_input = password + salt + repeat_to_length(b, len(password))

    # Bit manipulation loop
    i = len(password)
    while i > 0:
        a_input += b if i & 1 else password
        i >>= 1

    a = digest(a_input)

    # DP and DS calculations
    dp = digest(password * len(password))
    p = repeat_to_length(dp, len(password))
    ds = digest(salt * (16 + a[0]))
    s = repeat_to_length(ds, len(salt))

    # Main rounds of SHA512 crypt computation
    c = a
    for round_num in range(rounds):
        c_input = p if round_num & 1 else c
        if round_num % 3:
            c_input += s
        if round_num % 7:
            c_input += p
        c_input += c if round_num & 1 else p
        c = digest(c_input)

    # Final base64 encoding of the result
    hash_encoded = custom_b64_encode(c[:64])  # Only encode the first 64 bytes
    if rounds == ROUNDS_DEFAULT:
        return f"$6${salt.decode()}${hash_encoded}"
    return f"$6$rounds={rounds}${salt.decode()}${hash_encoded}"


def extract_salt_and_rounds(hash_str: str) -> tuple[bytes, int]:
    """Extract salt and rounds from a SHA-512 crypt hash."""
    if not hash_str.startswith("$6$"):
        raise TypeError("This function only supports $6$ hashes.")

    pieces = hash_str.split("$")

    if pieces[2].startswith("rounds="):
        rounds = max(1000, min(int(pieces[2][7:]), 999999999))  # Ensure rounds are within bounds
        salt = pieces[3]
    else:
        rounds = 5000  # Default rounds if not specified
        salt = pieces[2]

    return salt.encode("ascii"), rounds


def password_ok(input_password, existing_crypted_password):
    """Return if the password is ok."""
    (salt, rounds) = extract_salt_and_rounds(existing_crypted_password)
    return existing_crypted_password == sha512_crypt(input_password, salt, rounds)
