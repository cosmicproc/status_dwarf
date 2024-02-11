import unittest
from datetime import datetime, timedelta, timezone

from status_dwarf import create_app
from status_dwarf.models import session, Target, db


class TestModels(unittest.TestCase):

    def setUp(self):
        self.app = create_app(no_db=True, no_scheduler=True)
        self.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        db.init_app(self.app)
        with self.app.app_context():
            db.create_all()

    def test_add_timeline_item(self):
        with self.app.app_context():
            test_target = Target(name="Test Target", url="https://example.com")
            session.add(test_target)
            dt1 = datetime.now(timezone.utc)
            dt2 = dt1 + timedelta(days=1)
            test_target.add_timeline_item(dt1, dt2)
            self.assertEqual(test_target.head_timeline_item[0].datetime_start, dt1)
            self.assertEqual(test_target.head_timeline_item[0].datetime_end, dt2)

    def test_get_display_items(self):
        with self.app.app_context():
            test_target = Target(name="Test Target", url="https://example.com")
            session.add(test_target)
            self.assertEqual(len(test_target.get_display_items()),
                             self.app.config["STATUS_BLOCK_COUNT"])


if __name__ == '__main__':
    unittest.main()
