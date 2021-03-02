import unittest
import json
from app.extensions import db
from app.auth.models import History, User
from app.tests.base import BaseTestCase
from app.messages import RESOURCE_CREATION_SUCCESS
from app.api_paths import HISTORY_BASE_URL

class TestHistoryBlueprint(BaseTestCase):
    #API-touching methods
    def create_history(self, auth_token, name, type):
        return self.client.post(
            HISTORY_BASE_URL,
            headers=dict(
                Authorization='Bearer ' + auth_token
            ),
            data=json.dumps(dict(
                name=name,
                type=type,
            )),
            content_type='application/json',
        )
    def get_history(self,auth_token, history_id):
        return self.client.get(
            '/history/1/',
            headers=dict(
                Authorization='Bearer ' + auth_token
            ),
        )
    def register_user(self, username, email, password):
        return self.client.post(
            '/auth/register',
            data=json.dumps(dict(
                username=username,
                email=email,
                password=password
            )),
            content_type='application/json',
        )
    #test methods
    def test_create_history_without_entries(self):
        with self.client:
            #register user
            resp_register = self.register_user('joe', 'joe@gmail.com', '123456')
            data_register = json.loads(resp_register.data.decode())
            self.assertTrue(data_register['status'] == 'success')
            self.assertTrue(
                data_register['message'] == 'Successfully registered.'
            )
            self.assertTrue(data_register['auth_token'])
            self.assertTrue(resp_register.content_type == 'application/json')
            self.assertEqual(resp_register.status_code, 201)
            #create history
            auth_token = data_register['auth_token']
            response = self.create_history(auth_token,'Joe History','Pokemon')
            data = json.loads(response.data)
            expected_response = { "resource_uri": HISTORY_BASE_URL + '1' }
            self.assertTrue(data['status'] == 'success')
            self.assertTrue(data['message'] == expected_response)
            self.assertTrue(response.content_type == 'application/json')
            self.assertEqual(response.status_code, 201)

    def test_get_history(self):
        with self.client:
            #register user
            resp_register = self.register_user('joe', 'joe@gmail.com', '123456')
            data_register = json.loads(resp_register.data.decode())
            self.assertTrue(data_register['status'] == 'success')
            self.assertTrue(
                data_register['message'] == 'Successfully registered.'
            )
            self.assertTrue(data_register['auth_token'])
            self.assertTrue(resp_register.content_type == 'application/json')
            self.assertEqual(resp_register.status_code, 201)
            # create history
            auth_token = data_register['auth_token']
            response = self.create_history(auth_token,'Joe History','Pokemon')
            data = json.loads(response.data)
            expected_response = { "resource_uri": HISTORY_BASE_URL + '1' }
            self.assertTrue(data['status'] == 'success')
            self.assertTrue(data['message'] == expected_response)
            self.assertTrue(response.content_type == 'application/json')
            self.assertEqual(response.status_code, 201)
            #get history

if __name__ == '__main__':
    unittest.main()
