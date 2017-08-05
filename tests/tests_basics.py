import unittest
from datetime import datetime, timedelta
from flask import current_app
from app import create_app, db, utils


@unittest.skip
class BasicsTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app("testing")
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_app_exists(self):
        self.assertFalse(current_app is None)

    def test_app_is_testing(self):
        self.assertTrue(current_app.config["TESTING"])


class UtilsTestCase(unittest.TestCase):

    def setUp(self):
        self.hours = 24

    def test_is_in_last_x_hours(self):
        t = datetime.utcnow() - timedelta(hours=1)
        print(t)
        self.assertTrue(utils.is_within_last_x_hours(t, self.hours))

    def test_is_over_x_hours_ago(self):
        t = datetime.utcnow() - timedelta(hours=25)
        print(t)
        self.assertTrue(utils.is_over_x_hours_ago(t, self.hours))


if __name__ == "__main__":
    unittest.main()
