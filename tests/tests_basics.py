import unittest
from datetime import datetime, timedelta

from flask import current_app

from app import create_app, db, utils, models


class BasicsTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app("test")
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.db = db
        self.session = self.db.session
        self.models = models
        self.db.create_all()

    def tearDown(self):
        self.db.session.remove()
        self.db.drop_all()
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


class PaginationTestCase(unittest.TestCase):
    def setUp(self):
        self.thing1 = {'a': 1}
        self.thing2 = {'b': 2}
        self.thing3 = {'c': 3}
        self.thing4 = {'d': 4}
        self.thing5 = {'e': 5}
        self.all_items = [self.thing1, self.thing2, self.thing3, self.thing4, self.thing5]
        self.per_page = 2

    def test_pagination(self):
        p1 = [self.thing4, self.thing5]
        actual = utils.version_paginate(self.all_items, 1, self.per_page, len(self.all_items))
        self.assertTrue(p1 == actual)


class VersionIndexTestCase(BasicsTestCase):
    def test_version_index(self):
        tool = self.models.Tool(
            name="Foo"
        )

        self.session.add(tool)
        self.session.commit()
        tool.name = "Bar"
        self.session.commit()
        tool.name = "Baz"
        self.session.commit()
        assert tool.versions.count() == 3

        assert tool.versions[1].index == 1


class SoftDeleteTestCase(BasicsTestCase):
    def test_soft_delete(self):
        tool = self.models.Tool(name="Foo")
        self.session.add(tool)
        self.session.commit()

        before_query = self.models.Tool.query.filter_by(name="Foo").all()
        assert len(before_query) == 1

        tool.deleted = datetime.utcnow()
        self.session.commit()
        after_query = self.models.Tool.query.filter_by(name="Foo").all()
        assert len(after_query) == 0

        deleted_query = self.models.Tool.query.with_deleted().filter_by(name="Foo").all()
        assert len(deleted_query) == 1


if __name__ == "__main__":
    unittest.main()
