import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import scripts.sommelier as sommelier


class SommelierSmokeTest(unittest.TestCase):
    def test_main_generates_hosts_files_with_provenance(self):
        ipv4_results = [
            sommelier.SpeedResult(ip="1.1.1.1", latency_ms=10.0, success=True),
            sommelier.SpeedResult(ip="1.1.1.2", latency_ms=12.0, success=True),
        ]
        ipv6_results = [
            sommelier.SpeedResult(ip="2001:db8::1", latency_ms=20.0, success=True),
            sommelier.SpeedResult(ip="2001:db8::2", latency_ms=22.0, success=True),
        ]

        with tempfile.TemporaryDirectory() as tmpdir:
            old_cwd = os.getcwd()
            os.chdir(tmpdir)
            try:
                with mock.patch.dict(
                    os.environ,
                    {
                        "GITHUB_RUN_ID": "123456789",
                        "GITHUB_SHA": "abcdef1234567890fedcba",
                        "RUNNER_NAME": "JDCloud-FCM-Hosts-Next",
                    },
                    clear=False,
                ), mock.patch(
                    "scripts.sommelier.load_ips",
                    side_effect=[
                        ["1.1.1.10", "1.1.1.11"],
                        ["2001:db8::10", "2001:db8::11"],
                    ],
                ), mock.patch(
                    "scripts.sommelier.random.shuffle",
                    side_effect=lambda seq: None,
                ), mock.patch.object(
                    sommelier.AdaptiveSelector,
                    "expand_and_rescan",
                    side_effect=[ipv4_results, ipv6_results],
                ):
                    sommelier.main()
            finally:
                os.chdir(old_cwd)

            dual_hosts = Path(tmpdir, "fcm_dual.hosts")
            ipv4_hosts = Path(tmpdir, "fcm_ipv4.hosts")
            ipv6_hosts = Path(tmpdir, "fcm_ipv6.hosts")

            self.assertTrue(dual_hosts.exists())
            self.assertTrue(ipv4_hosts.exists())
            self.assertTrue(ipv6_hosts.exists())

            content = dual_hosts.read_text()
            self.assertIn("# Workflow Run: 123456789", content)
            self.assertIn("# Commit: abcdef123456", content)
            self.assertIn("# Verified On: JDCloud-FCM-Hosts-Next", content)
            self.assertIn("# Seeds: IPv4=2, IPv6=2", content)
            self.assertIn("# Selected: IPv4=2, IPv6=2", content)
            self.assertIn("mtalk.google.com", content)


if __name__ == "__main__":
    unittest.main()
