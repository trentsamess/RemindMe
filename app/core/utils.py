import binascii
import json

from Crypto.Cipher import DES
from django.core.serializers.json import DjangoJSONEncoder
from rest_framework.exceptions import ValidationError

from config import settings


class Crypter:
    PAT_BIT = 8
    KEY = settings.SECRET_KEY
    LENGTH_KEY = (0, 8)
    crypt_alg = DES
    crypt_mode = DES.MODE_ECB

    @classmethod
    def pat(cls, data: bytes):
        while len(data) % cls.PAT_BIT != 0:
            data += b' '
        return data

    @classmethod
    def _get_crypt_key(cls):
        return cls.KEY[cls.LENGTH_KEY[0]:cls.LENGTH_KEY[1]].encode()

    @classmethod
    def crypt_data(cls, data, _hex=True):
        data = cls.pat(data.encode())
        crypter = cls.get_crypt()
        return crypter.encrypt(data).hex() if _hex else crypter.encrypt(data)

    @classmethod
    def decrypt_data(cls, data, _hex=True):
        try:
            if _hex:
                data = binascii.unhexlify(data)
            crypter = cls.get_crypt()
            result = crypter.decrypt(data).decode()
        except Exception:
            raise ValidationError('Invalid token')
        return result

    @classmethod
    def get_data_from_code(cls, token, fields='__all__') -> dict:
        if not token:
            return {}
        token_data = json.loads(cls.decrypt_data(token)) or {}
        if isinstance(fields, list):
            return {field: token_data.get(field, None) for field in fields}
        elif isinstance(fields, str):
            return token_data if fields == '__all__' else {}

    @classmethod
    def get_crypt(cls):
        return cls.crypt_alg.new(cls._get_crypt_key(), cls.crypt_mode)


class TokenCrypter(Crypter):
    pass


class TokenGenerator:
    crypter = TokenCrypter()

    @classmethod
    def create_email_activation_token(cls, user):
        data = {
            'user_id': user.id,
            'type': 'email_activate'
        }
        return cls.crypter.crypt_data(json.dumps(data, cls=DjangoJSONEncoder))
