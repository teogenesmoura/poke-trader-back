import unittest
import os
from app.extensions import db
from app.auth.models import User
from app.tests.base import BaseTestCase
from app.util.util import encode_auth_token, decode_auth_token

class TestUserModel(BaseTestCase):
    def test_encode_auth_token(self):
        user = User(
            username='test',
            email='test@test.com',
            password= 'test'
        )
        db.session.add(user)
        db.session.commit()
        auth_token = encode_auth_token(user.id)
        self.assertTrue(isinstance(auth_token, str))

    def test_decode_auth_token(self):
        user = User(
            username='test',
            email='test@test.com',
            password='test'
        )
        db.session.add(user)
        db.session.commit()
        auth_token = encode_auth_token(user.id)
        self.assertTrue(isinstance(auth_token, str))
        self.assertTrue(decode_auth_token(auth_token) == 1)

if __name__ == '__main__':
    unittest.main()
