import asyncio
import unittest

import httpx

from status_dwarf.monitor import http_heartbeat, icmp_heartbeat


class TestMonitor(unittest.TestCase):
    def test_http_heartbeat(self):
        test_target = "https://google.com"
        self.assertEqual(asyncio.run(http_heartbeat(test_target)),
                         httpx.get(test_target).status_code < 400)

    def test_icmp_heartbeat(self):
        test_targets = ["8.8.8.8", "https://google.com"]
        # Here we assume that these targets are always up.
        for target in test_targets:
            self.assertEqual(asyncio.run(icmp_heartbeat(target)), True)


if __name__ == '__main__':
    unittest.main()
