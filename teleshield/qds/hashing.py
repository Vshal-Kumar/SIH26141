"""
QDS Message Hashing and Binding Module
Supports two message binding mechanisms:
  Mode 1: SHA-256 (cryptographic hash; computationally collision-resistant;
                   NOT information-theoretically secure)
  Mode 2: Toeplitz / Epsilon-Almost-Universal (EAU) hashing over GF(2)
                   (information-theoretically bounded universal hash family)
"""

from __future__ import annotations
from enum import Enum
from typing import Tuple, List, Optional
import hashlib
import numpy as np


class HashMode(str, Enum):
    SHA256 = "sha256"
    TOEPLITZ = "toeplitz"


def string_to_bits(s: str) -> List[int]:
    """Convert UTF-8 string to list of bits."""
    data = s.encode("utf-8")
    bits = []
    for byte in data:
        for i in range(7, -1, -1):
            bits.append((byte >> i) & 1)
    return bits


def sha256_bind(message: str, n_bits: int) -> Tuple[str, List[int]]:
    """
    Message binding using SHA-256.
    NOTE: SHA-256 relies on computational hardness assumptions (collision resistance,
    preimage resistance). It does NOT provide information-theoretic security.
    Truncates or expands the hash to n_bits.
    """
    hasher = hashlib.sha256()
    hasher.update(message.encode("utf-8"))
    hex_digest = hasher.hexdigest()

    # Convert hex digest to bits
    full_bits = []
    for char in hex_digest:
        val = int(char, 16)
        for i in range(3, -1, -1):
            full_bits.append((val >> i) & 1)

    # Truncate or repeat if n_bits differs from 256
    if len(full_bits) >= n_bits:
        tag_bits = full_bits[:n_bits]
    else:
        # Repeat hash deterministically if n_bits > 256
        tag_bits = []
        counter = 0
        while len(tag_bits) < n_bits:
            sub = hashlib.sha256(f"{message}_{counter}".encode("utf-8")).hexdigest()
            for char in sub:
                val = int(char, 16)
                for i in range(3, -1, -1):
                    tag_bits.append((val >> i) & 1)
                    if len(tag_bits) == n_bits:
                        break
                if len(tag_bits) == n_bits:
                    break
            counter += 1

    # Hex representation of tag_bits
    hex_chars = []
    for i in range(0, len(tag_bits), 4):
        chunk = tag_bits[i:i+4]
        val = 0
        for b in chunk:
            val = (val << 1) | b
        hex_chars.append(f"{val:x}")
    tag_hex = "".join(hex_chars)

    return tag_hex, tag_bits


def toeplitz_bind(
    message: str,
    n_bits: int,
    seed: int = 1337,
) -> Tuple[str, List[int]]:
    """
    Message binding using a Toeplitz matrix over GF(2).
    Toeplitz matrix multiplication T * x mod 2 constitutes a universal
    hash family with bounded collision probability epsilon <= 2^{-n}.
    Provides information-theoretic security bounds when evaluated against
    bounded quantum adversaries.
    """
    msg_bits = string_to_bits(message)
    if len(msg_bits) == 0:
        msg_bits = [0]

    m_len = len(msg_bits)
    # Toeplitz matrix T of dimension (n_bits x m_len) is defined by (n_bits + m_len - 1) random bits
    rng = np.random.default_rng(seed)
    random_seq = rng.integers(0, 2, size=(n_bits + m_len - 1))

    # Construct and multiply T * msg_bits over GF(2)
    # T[i, j] = random_seq[i - j + m_len - 1]
    tag_bits = []
    x = np.array(msg_bits, dtype=np.uint8)
    for i in range(n_bits):
        row = random_seq[i : i + m_len][::-1]
        dot_product = int(np.sum(row * x) % 2)
        tag_bits.append(dot_product)

    # Hex representation
    hex_chars = []
    for i in range(0, len(tag_bits), 4):
        chunk = tag_bits[i:i+4]
        val = 0
        for b in chunk:
            val = (val << 1) | b
        hex_chars.append(f"{val:x}")
    tag_hex = "".join(hex_chars)

    return tag_hex, tag_bits


def compute_message_tag(
    message: str,
    mode: HashMode = HashMode.SHA256,
    n_bits: int = 64,
    toeplitz_seed: int = 1337,
) -> Tuple[str, List[int]]:
    """
    Computes message tag and bit array according to configured HashMode.
    """
    if mode == HashMode.SHA256:
        return sha256_bind(message, n_bits)
    elif mode == HashMode.TOEPLITZ:
        return toeplitz_bind(message, n_bits, seed=toeplitz_seed)
    raise ValueError(f"Unsupported hash mode: {mode}")


def verify_message_tag(
    message: str,
    claimed_tag_bits: List[int],
    mode: HashMode = HashMode.SHA256,
    n_bits: int = 64,
    toeplitz_seed: int = 1337,
) -> bool:
    """Verifies that claimed_tag_bits match the message hash."""
    _, expected_bits = compute_message_tag(
        message=message,
        mode=mode,
        n_bits=n_bits,
        toeplitz_seed=toeplitz_seed,
    )
    return claimed_tag_bits == expected_bits
