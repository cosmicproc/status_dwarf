import asyncio
import unittest

import httpx

from status_dwarf.monitor import is_url_up


class TestMonitor(unittest.TestCase):
    def test_is_url_up(self):
        test_target = "https://google.com"
        self.assertEqual(asyncio.run(is_url_up(test_target)),
                         httpx.get(test_target).status_code < 400)


if __name__ == '__main__':
    unittest.main()
