import unittest
from ky_parser import KYParser

class TestKYGrammar(unittest.TestCase):
    def setUp(self):
        self.parser = KYParser()

    def test_valid_open(self):
        # Full validation with audit
        res = self.parser.evaluate("☑(○→◇→□→O→•)#! ►")
        self.assertEqual(res.syntax, 'valid')
        self.assertEqual(res.type_status, 'valid')
        self.assertEqual(res.gate, 'OPEN')

    def test_valid_hold(self):
        # Structural hold
        res = self.parser.evaluate("(□~O) ⏸")
        self.assertEqual(res.gate, 'HOLD')
        self.assertEqual(res.admissibility, 'hold')

    def test_invalid_syntax(self):
        # Missing parens
        res = self.parser.evaluate("○→◇ ►")
        self.assertEqual(res.syntax, 'invalid')
        self.assertEqual(res.gate, 'KILL')

    def test_type_error_shortcut(self):
        # Direct jump from RAW to COMMITTED
        res = self.parser.evaluate("(○→•) X")
        self.assertEqual(res.type_status, 'invalid')
        self.assertIn('Type Error', res.reasons[0])
        self.assertEqual(res.gate, 'KILL')

    def test_irreversible_without_audit(self):
        # Reaches COMMITTED but lacks '#' or '!'
        res = self.parser.evaluate("(□→O→•) ►")
        # Should fail-closed due to Gate Mismatch & Audit Law
        self.assertEqual(res.gate, 'KILL')
        self.assertTrue(any("Audit Law Violation" in r for r in res.reasons))

    def test_inadmissible_override(self):
        # Structurally fine, but flagged ∉K
        res = self.parser.evaluate("(○→◇)∉K X")
        self.assertEqual(res.gate, 'KILL')
        self.assertTrue(any("Inadmissible mark" in r for r in res.reasons))

    def test_gate_mismatch(self):
        # Valid chain, but claims KILL instead of OPEN/HOLD, or invalid claims OPEN
        res = self.parser.evaluate("(○→•)X ►") # Syntax is weird here based on regex, let's do a logic mismatch
        res2 = self.parser.evaluate("(○→◇)∉K ►")
        self.assertEqual(res2.gate, 'KILL')
        self.assertTrue(any("Gate Mismatch" in r for r in res2.reasons))

if __name__ == '__main__':
    unittest.main(verbosity=2)
