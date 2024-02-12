import unittest

from status_dwarf import create_app


class TestViews(unittest.TestCase):
    def setUp(self):
        self.app = create_app(no_scheduler=True)
        self.app.testing = True
        self.client = self.app.test_client()

    def test_index(self):
        # Assure that home page is accessible
        request = self.client.get("/")
        self.assertEqual(request.status_code, 200)

    def test_atom(self):
        addresses = ["/atom", "/atom.xml"]
        requests = (self.client.get(address) for address in addresses)
        is_atom_enabled = self.app.config["ATOM_ENABLED"]
        for request in requests:
            self.assertEqual(request.status_code, 404 if not is_atom_enabled else 200)


if __name__ == '__main__':
    unittest.main()
