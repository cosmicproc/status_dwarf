import unittest
from datetime import datetime, timedelta

from status_dwarf import utils


class TestUtils(unittest.TestCase):
    def test_div_ceil(self):
        self.assertEqual(utils.div_ceil(3, 2), 2)
        self.assertEqual(utils.div_ceil(2, 2), 1)
        self.assertEqual(utils.div_ceil(1, 2), 1)

    def test_sub_datetime_rounded(self):
        dt1 = datetime.now().replace(microsecond=0)
        dt2 = dt1 + timedelta(microseconds=950000)
        self.assertEqual(utils.sub_datetime_rounded(dt2, dt1), timedelta(seconds=1))

    def test_strip_protocol(self):
        tests = {
            "https://example.com": "example.com",
            "http://example.com": "example.com",
            "example.com": "example.com",
        }
        for address, expected in tests.items():
            self.assertEqual(utils.strip_protocol(address), expected)

    def test_translator(self):
        # _("") pattern should not be used here as it would be caught by i18n base generation script.
        class PseudoApp:
            config = {"TRANSLATIONS_ENABLED": False}

        utils.current_app = PseudoApp
        trans = utils.Translator()
        self.assertEqual(trans("Hello"), "Hello")

        PseudoApp.config["TRANSLATIONS_ENABLED"] = True
        trans.get_lang = lambda: "en"
        self.assertEqual(trans("Hello"), "Hello")

        trans.i18n = {"es": {"Hello": "Hola"}}
        trans.get_lang = lambda: "es"
        self.assertEqual(trans("Hello"), "Hola")


if __name__ == '__main__':
    unittest.main()
