import urllib.parse
import http.client
import json

from Crypto import Random
from Crypto.Cipher import AES
import base64
from hashlib import md5

from config import ap_url
from payment_gateway import Ap_Payment_Gateway


class Ap_Locker:
    def __init__(self):
        self._block_size = 16
        self._password = "12e702f424dbd7d351be709a7972f9a58e9e".encode()

    def get_password(self):
        # efficient approach would be to regenerate a password every time.
        return self._password.decode()

    def pad(self, data):
        length = self._block_size - (len(data) % self._block_size)
        return data + (chr(length)*length).encode()

    def unpad(self, data):
        return data[:-(data[-1] if type(data[-1]) == int else ord(data[-1]))]

    def bytes_to_key(self, data, salt, output=48):
        assert len(salt) == 8, len(salt)
        data += salt
        key = md5(data).digest()
        final_key = key
        while len(final_key) < output:
            key = md5(key + data).digest()
            final_key += key
        return final_key[:output]

    def encrypt(self, message):
        passphrase = self._password
        salt = Random.new().read(8)
        key_iv = self.bytes_to_key(passphrase, salt, 32+16)
        key = key_iv[:32]
        iv = key_iv[32:]
        aes = AES.new(key, AES.MODE_CBC, iv)
        return base64.b64encode(b"Salted__" + salt + aes.encrypt(self.pad(message)))

    def decrypt(self, encrypted):
        passphrase = self._password
        encrypted = base64.b64decode(encrypted)
        assert encrypted[0:8] == b"Salted__"
        salt = encrypted[8:16]
        key_iv = self.bytes_to_key(passphrase, salt, 32+16)
        key = key_iv[:32]
        iv = key_iv[32:]
        aes = AES.new(key, AES.MODE_CBC, iv)
        return self.unpad(aes.decrypt(encrypted[16:]))

    def get_token(self, data=""):
        # efficient approach would be to store token, encrypted card number, timestamp in a database.
        return "ap_token-"+md5(data.encode()).hexdigest()

    def detokenize(self, form_data={}):
        retoken = self.get_token(data=form_data["card_number"])

        # efficient approach would be to compare the token in a database and allow access if the token matches and within a specified time frame eg: within 2 minutes
        if retoken == form_data["token"]:
            try:
                data = form_data
                data["card_number"] = self.decrypt(form_data["card_number"]).decode()

                # process payment without API call
                # return Ap_Payment_Gateway.process(data)

                conn = http.client.HTTPConnection(ap_url)
                payload = urllib.parse.urlencode(data)
                headers = {'Content-Type': "application/x-www-form-urlencoded"}
                conn.request("POST", "/payment_gateway/process", payload, headers)
                res = conn.getresponse()
                data = res.read()
                return json.loads(data.decode("utf-8"))
            except Exception as e:
                return {"status": 400, "message": "Oops!! Something went wrong with the payment."}
        else:
            return {"status": 400, "message": "token did not match"}
        pass

if __name__ == "__main__":
   # refrenced from https://stackoverflow.com/questions/36762098/how-to-decrypt-password-from-javascript-cryptojs-aes-encryptpassword-passphras

    ct_b64 = "U2FsdGVkX18RFUJudPpwkrO0GCguCfrGIFxzPXd4Ciw5jdjCH0Oh9Qxm7aYF3fQe"
    ap = Ap_Locker()
    pt = ap.decrypt(ct_b64)
    print("pt", pt)
    print(ap.get_token(ct_b64))

