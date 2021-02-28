from flask_testing import TestCase
from app import create_app
from app.extensions import db

class BaseTestCase(TestCase):
    """ Base Tests """

    def create_app(self):
        app = create_app()
        app.config.from_object('app.config.TestingConfig')
        return app

    def setUp(self):
        db.create_all()
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
