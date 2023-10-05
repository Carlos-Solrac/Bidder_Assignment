"""

Name: Carlos Cuellar
Date: 10/22/22
Assignment: 8
Due Date:10/3/22
About this project: Develop code that encrypts data stored in a database for a  small scale  using third-party Python
libraries discussed in the course. Use this database to send encrypted messages with HMAC authentication to a python created server.
Assumptions: Assume correct input.
All work below was performed by Carlos Cuellar
"""

from Crypto.Cipher import AES
import string, base64


class AEScipher(object):
    def __init__(self, key, iv):
        self.key = key
        self.iv = iv

    def encrypt(self, raw):
        self.cipher = AES.new(self.key, AES.MODE_CFB, self.iv)
        ciphertext = self.cipher.encrypt(raw)
        encoded = base64.b64encode(ciphertext)
        return encoded

    def decrypt(self, raw):
        decoded = base64.b64decode(raw)
        self.cipher = AES.new(self.key, AES.MODE_CFB, self.iv)
        decrypted = self.cipher.decrypt(decoded)
        return str(decrypted, 'utf-8')


key = b'Las12fF2321asfdB21fsaddsfgs55A3!'
iv = b'WOS12aJKSF132asd'

cipher = AEScipher(key, iv)
