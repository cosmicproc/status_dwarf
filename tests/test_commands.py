import unittest

from status_dwarf import create_app, db
from status_dwarf.commands import sync_targets
from status_dwarf.models import Target, session


class TestCommands(unittest.TestCase):
    def test_sync_targets(self):
        app = create_app(no_db=True, no_scheduler=True)
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        test_targets = [
            ("Example 1", "https://example.com"),
            ("Example 2", "https://example.com"),
            ("Example 3", "https://example.com"),
        ]
        app.config["TARGETS"] = test_targets
        db.init_app(app)
        with app.app_context():
            db.create_all()
            sync_targets(no_confirm=True)
            for target in session.query(Target).all():
                self.assertEqual(target.name, test_targets[target.id - 1][0])
                self.assertEqual(target.address, test_targets[target.id - 1][1])


if __name__ == '__main__':
    unittest.main()
