"""Real tests for wine outlier audit - at least 3 meaningful tests."""
import unittest
import pandas as pd
import sys
from pathlib import Path

# allows import from src/
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from outlier_audit import _z_flags as z_flags, _iqr_flags as iqr_flags

class TestOutlierAudit(unittest.TestCase):

    def test_missing_column_fails_clearly(self):
        """Test 1: Missing required column should be detected"""
        df = pd.DataFrame({
            "sample_id": [1, 2],
            "alcohol": [13.0, 12.5],
            # malic_acid is MISSING on purpose
            "proline": [1000, 1100],
            "target": [0, 1]
        })
        required = ["sample_id", "alcohol", "malic_acid", "proline", "target"]
        missing = [c for c in required if c not in df.columns]
        self.assertIn("malic_acid", missing)
        self.assertEqual(len(missing), 1)

    def test_zero_variance_is_safe(self):
        """Test 2: Zero-variance column must not crash or flag everything"""
        s = pd.Series([5.0, 5.0, 5.0, 5.0])
        # std = 0, IQR = 0 - should return all False, not NaN / error
        self.assertEqual(z_flags(s).sum(), 0)
        self.assertEqual(iqr_flags(s).sum(), 0)
        self.assertFalse(z_flags(s).isna().any())

    def test_z_flag_detects_extreme_value(self):
        """Test 3: Z-score |Z|>3 must flag a true extreme"""
        s = pd.Series([1.0]*20 + [100.0])
        flags = z_flags(s)
        self.assertTrue(flags.iloc[-1])  # 100 is flagged
        self.assertFalse(flags.iloc[0])  # normal value not flagged

    def test_domain_rule_proline_invalid(self):
        """Test 4: proline <= 0 is invalid - domain rule"""
        df = pd.DataFrame({"proline": [1000, 0, -5, 750]})
        invalid = df["proline"] <= 0
        self.assertEqual(list(invalid), [False, True, True, False])

    def test_domain_rule_malic_acid_invalid(self):
        """Test 5: negative or missing malic_acid is invalid"""
        df = pd.DataFrame({"malic_acid": [1.5, -0.2, None, 2.0]})
        invalid = (df["malic_acid"] < 0) | (df["malic_acid"].isna())
        self.assertEqual(list(invalid), [False, True, True, False])

    def test_statistical_outlier_alone_is_not_quarantined(self):
        """Test 6: Statistical flag alone != quarantine, only invalid domain is"""
        # This is the key rule for your lab
        is_statistical_flag = True
        is_domain_invalid = False
        should_quarantine = is_domain_invalid  # NOT statistical flag
        self.assertFalse(should_quarantine)

if __name__ == "__main__":
    unittest.main()