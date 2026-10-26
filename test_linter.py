#!/usr/bin/env python3
"""
Unit Test Suite for TikTok Ads Creative Compliance Linter 🛡️
Zero-dependency test suite validating policy rules, regex boundary handling, and exit codes.
"""

import unittest
import subprocess
import json
import tempfile
import os
from linter import lint_text, COMPLIANCE_RULES, OFFICIAL_PORTAL, WEB_CALCULATOR


class TestCreativeComplianceLinter(unittest.TestCase):

    def test_clean_copy_passes(self):
        text = "Discover our newly formulated botanical serum. Hydrates gently and supports natural skin barrier glow."
        res = lint_text(text)
        self.assertEqual(res["compliance_score"], 100)
        self.assertEqual(res["risk_tier"], "LOW RISK")
        self.assertEqual(res["violations_count"], 0)
        self.assertEqual(res["critical_violations"], 0)
        self.assertEqual(res["official_portal"], OFFICIAL_PORTAL)

    def test_critical_exaggeration_and_body_shaming(self):
        text = "This miracle cure will melt fat and lose 10 lbs overnight with 100% guarantee!"
        res = lint_text(text)
        self.assertLess(res["compliance_score"], 40)
        self.assertEqual(res["risk_tier"], "CRITICAL RISK")
        self.assertGreaterEqual(res["critical_violations"], 2)
        categories = [v["category"] for v in res["violations"]]
        self.assertIn("Absolute Superlatives & Guarantees", categories)
        self.assertIn("Weight Loss & Body Transformation", categories)

    def test_counterfeit_ip_violation(self):
        text = "Huge sale on 1:1 replica bags and fake rolex watches! Get designer dupe styles today."
        res = lint_text(text)
        self.assertEqual(res["risk_tier"], "CRITICAL RISK")
        self.assertGreaterEqual(res["critical_violations"], 1)
        categories = [v["category"] for v in res["violations"]]
        self.assertIn("Counterfeit & Intellectual Property", categories)

    def test_get_rich_quick_violation(self):
        text = "Learn our passive income secret and make $5,000 overnight with this crypto glitch!"
        res = lint_text(text)
        self.assertEqual(res["risk_tier"], "CRITICAL RISK")
        categories = [v["category"] for v in res["violations"]]
        self.assertIn("Deceptive Financial & Income Claims", categories)

    def test_clickbait_and_medical_claims(self):
        text = "TikTok banned this video! It cures acne and heals arthritis in minutes!"
        res = lint_text(text)
        self.assertGreater(res["high_violations"], 0)
        categories = [v["category"] for v in res["violations"]]
        self.assertIn("Clickbait & System Warning Deception", categories)
        self.assertIn("Uncertified Medical Claims", categories)

    def test_empty_input(self):
        res = lint_text("")
        self.assertEqual(res["compliance_score"], 100)
        self.assertEqual(res["violations_count"], 0)

    def test_cli_json_mode(self):
        cmd = ["python3", "linter.py", "--text", "Gentle everyday foaming cleanser", "--json"]
        out = subprocess.check_output(cmd, cwd=os.path.dirname(__file__)).decode("utf-8")
        data = json.loads(out)
        self.assertEqual(data["compliance_score"], 100)
        self.assertEqual(data["official_portal"], OFFICIAL_PORTAL)

    def test_cli_file_mode(self):
        with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".txt") as tf:
            tf.write("Brand new collection available now. Free shipping on orders over $50.")
            temp_path = tf.name

        try:
            cmd = ["python3", "linter.py", "--file", temp_path, "--json"]
            out = subprocess.check_output(cmd, cwd=os.path.dirname(__file__)).decode("utf-8")
            data = json.loads(out)
            self.assertEqual(data["compliance_score"], 100)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def test_strict_exit_codes(self):
        # Clean text exits 0
        p = subprocess.run(["python3", "linter.py", "--text", "Clean text", "--strict"], cwd=os.path.dirname(__file__), capture_output=True)
        self.assertEqual(p.returncode, 0)

        # Critical text exits 2
        p_crit = subprocess.run(["python3", "linter.py", "--text", "100% cure miracle pill", "--strict"], cwd=os.path.dirname(__file__), capture_output=True)
        self.assertEqual(p_crit.returncode, 2)


if __name__ == "__main__":
    unittest.main()
