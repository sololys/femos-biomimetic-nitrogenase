"""
Rosetta³: Trit-to-Bit Compiler v0.1
Kanonisk oversettelse for E-TOR² / Phronesis fail-closed gating.

Semantic layer:
    KILL = -1
    HOLD =  0
    OPEN = +1

Binary enforcement:
    00 = KILL
    01 = HOLD
    10 = OPEN
    11 = INVALID -> KILL
"""


class RosettaCompiler:
    KILL = -1
    HOLD = 0
    OPEN = 1

    VALID_TRITS = {KILL, HOLD, OPEN}

    ENCODING = {
        KILL: "00",
        HOLD: "01",
        OPEN: "10",
    }

    DECODING = {
        "00": KILL,
        "01": HOLD,
        "10": OPEN,
        "11": KILL,  # illegal binary state -> fail-closed
    }

    @staticmethod
    def trit_to_binary(trit):
        """Compile one trit to binary. Invalid input becomes KILL."""
        if type(trit) is not int:
            return "00"

        return RosettaCompiler.ENCODING.get(trit, "00")

    @staticmethod
    def binary_to_trit(bits):
        """Decode binary to trit. Invalid binary becomes KILL."""
        return RosettaCompiler.DECODING.get(bits, RosettaCompiler.KILL)

    @staticmethod
    def compile_gate(trits):
        """
        Fail-closed ternary gate.

        Rule:
        - Any invalid input -> KILL
        - Any KILL -> KILL
        - Else any HOLD -> HOLD
        - Else OPEN
        """
        if not isinstance(trits, list):
            return "00"

        if len(trits) == 0:
            return "00"

        for trit in trits:
            if type(trit) is not int:
                return "00"
            if trit not in RosettaCompiler.VALID_TRITS:
                return "00"

        tau_total = min(trits)
        return RosettaCompiler.ENCODING[tau_total]


if __name__ == "__main__":
    c = RosettaCompiler()

    cases = [
        ("ALL_OPEN", [c.OPEN, c.OPEN, c.OPEN], "10"),
        ("HOLD_DOMINATES", [c.OPEN, c.HOLD, c.OPEN], "01"),
        ("KILL_DOMINATES", [c.OPEN, c.KILL, c.OPEN], "00"),
        ("INVALID_POSITIVE_TRIT", [c.OPEN, c.OPEN, 2], "00"),
        ("INVALID_NEGATIVE_TRIT", [c.OPEN, c.OPEN, -2], "00"),
        ("EMPTY_INPUT", [], "00"),
        ("NON_LIST_INPUT", "OPEN", "00"),
        ("NON_INT_INPUT", [c.OPEN, "HOLD", c.OPEN], "00"),
    ]

    for name, trits, expected in cases:
        result = c.compile_gate(trits)
        print(f"{name}: trits={trits}, binary={result}, expected={expected}")
        assert result == expected, f"{name}: expected {expected}, got {result}"

    decode_cases = [
        ("DECODE_KILL", "00", c.KILL),
        ("DECODE_HOLD", "01", c.HOLD),
        ("DECODE_OPEN", "10", c.OPEN),
        ("DECODE_INVALID_11", "11", c.KILL),
        ("DECODE_INVALID_TEXT", "xx", c.KILL),
    ]

    for name, bits, expected in decode_cases:
        result = c.binary_to_trit(bits)
        print(f"{name}: bits={bits}, trit={result}, expected={expected}")
        assert result == expected, f"{name}: expected {expected}, got {result}"

    print("ROSETTA_TRIT_TO_BIT_COMPILER_PASS")
