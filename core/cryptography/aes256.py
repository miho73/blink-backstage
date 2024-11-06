import base64
from secrets import token_bytes

from Crypto.Cipher import AES

key = token_bytes(32)

def encrypt(plain_text: str):
    cipher = AES.new(key, AES.MODE_EAX)
    nonce = cipher.nonce
    ciphertext, tag = cipher.encrypt_and_digest(bytes(plain_text, 'utf-8'))

    encrypted = (base64.b64encode(nonce).decode('ascii') + '!'
                 + base64.b64encode(ciphertext).decode('ascii') + '!'
                 + base64.b64encode(tag).decode('ascii'))

    return encrypted

def decrypt(encrypted: str):
    [s_nonce, s_ciphertext, s_tag] = encrypted.split('!')

    nonce = base64.b64decode(s_nonce)
    ciphertext = base64.b64decode(s_ciphertext)
    tag = base64.b64decode(s_tag)

    cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)
    plaintext = cipher.decrypt(ciphertext)
    try:
        cipher.verify(tag)
        return plaintext.decode('ascii')
    except:
        return None
