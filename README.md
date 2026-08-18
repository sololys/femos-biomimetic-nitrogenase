# 🧪 Fe-Mo-S Biomimetic Nitrogenase & Electrocatalytic Validation Engine
### Deterministic Validation and Fail-Closed Control for Bio-Inorganic Catalyst & Hydrogen Pilot Systems

[![CI Validation](https://github.com/sololys/femos-biomimetic-nitrogenase/actions/workflows/ci.yml/badge.svg)](https://github.com/sololys/femos-biomimetic-nitrogenase/actions/workflows/ci.yml)
[![Portfolio Hub](https://img.shields.io/badge/Portfolio%20Hub-sololys%2Fsololys-blueviolet)](https://github.com/sololys/sololys)
[![ORCID](https://img.shields.io/badge/ORCID-0009--0006--0431--6637-green.svg)](https://orcid.org/0009-0006-0431-6637)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-blue)](https://www.python.org/)

* **Portfolio Hub:** [sololys / sololys](https://github.com/sololys/sololys)
* **Author:** Marius Egerhei Torjusen (ORCID: [0009-0006-0431-6637](https://orcid.org/0009-0006-0431-6637))
* **Entity:** ReismannPoint Systems AS // Kreativ Systems ([kreativ-systems.org](https://kreativ-systems.org/))
* **Target Audience:** Universitetet i Oslo (UiO), SINTEF Industry, NTNU, and Industrial Process Partners
* **Status:** Exploratory // Feasibility Dialogue & Benchmarking Suite

---

## 🏛️ 1. Purpose & Core Problem

This repository provides an open-science deterministic validation engine and fail-closed control protocol for anaerobic bio-inorganic catalyst systems and electrochemical nitrogen fixation ($N_2 \to NH_3$).

### The Central Challenge in Catalysis R&D:
In novel catalyst screening, promising local signals or predictive simulations are frequently allowed to guide expensive physical laboratory trials before causal, isotopic, and material validity is rigorously proven. This leads to **false positives, contamination misinterpretations (atmospheric amine/nitrate artifacts), and severe R&D resource waste**.

### The Solution: The 4-Layer Admissibility Architecture
We strictly separate **candidate generation** from **authorized physical actuation**:

$$\text{Measurement} \longrightarrow \text{Raw Evidence} \longrightarrow \text{Candidate} \longrightarrow \Pi_K \text{ (Admissibility Test)} \longrightarrow \text{Authorized Actuation (5.0V / 0.0V)}$$

$$\boxed{\mathbf{x_{t+1} = \Pi_K(f(x_t, u_t))}}$$

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│ LAYER 1: RAW EVIDENCE CAPTURE                                               │
│ • Sensor traces, Mössbauer baseline, Raman in situ, CV, GC-MS blanks, logs.  │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼ (Evidence streamed)
┌─────────────────────────────────────────────────────────────────────────────┐
│ LAYER 2: ESTIMATION & CANDIDATE GENERATION                                  │
│ • Predictive control, digital twin, empirical bond predictor (Pauling-Morse).│
│ • Proposes setpoint / candidate (Does NOT authorise!).                      │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼ (Candidate tested)
┌─────────────────────────────────────────────────────────────────────────────┐
│ LAYER 3: ADMISSIBILITY TESTING (Π_K)                                        │
│ • Causal validity (H/D KIE ≥ 5.0), spectral integrity, perturbation recovery.│
│ • Thermal (dT/dt), pressure (dP/dt), and degradation/side-reaction bounds.  │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
          ┌────────────────────────────┴────────────────────────────┐
          ▼ (Admissible: PASS)                                      ▼ (Violation: REJECT / KILL)
┌──────────────────────────────────────┐                  ┌──────────────────────────────────────┐
│ LAYER 4: AUTHORISED ACTUATION (5.0V) │                  │ HARDWARE LATCH / SHUTDOWN (0.0V)     │
│ • Safety relay closes, solenoid      │                  │ • Hard shutoff, inert purge, power   │
│   opens, physical action permitted.  │                  │   cut, latched stop (No auto-retry). │
└──────────────────────────────────────┘                  └──────────────────────────────────────┘
```

---

## 🔬 2. PROTOKOLL Fe-Mo-S Validation Standards

The complete protocol is specified in [`PROTOKOLL_FE_MO_S.md`](PROTOKOLL_FE_MO_S.md) and enforces three rigorous parts:

### Part I: Chemical Architecture & Structural Integrity
* **Strict Anaerobic Regime:** $O_2 < 1.0\text{ ppm}$, $H_2O < 1.0\text{ ppm}$ (prevents $\text{Fe-O-Fe}$ oxo-bridges).
* **Stoichiometric Tolerance (ICP-OES):** $\le \pm 2.5\%$ deviation.
* **Mössbauer Isomer Shift (80 K Target):** $\text{Fe}^{\text{II}}\text{-site}$ $\delta = 0.45 \pm 0.03\text{ mm/s}$ ($\Delta E_Q = 2.10 \pm 0.15\text{ mm/s}$).
* **Cathodic Reduction Window:** $E_{\text{cat}} \in [-1.45\text{ V}, -1.65\text{ V}]$ vs $\text{Fc/Fc}^+$ (Potentials more negative than $-1.65\text{ V}$ are killed due to HER dominance).

### Part II: Causality & Anti-Self-Deception Spectroscopic Gates
* **Kinetic Isotope Effect (KIE):** Mandatory $H/D$ $\text{KIE} = k_H / k_D \ge 5.0$ proving Proton-Coupled Electron Transfer (PCET) is rate-determining.
* **Operando In Situ Raman/IR:** Overviews diazenido $\text{Fe-N=NH}$ formation at $\sim 1490\text{ cm}^{-1}$ under $^{15}N_2$.
* **$^{15}N\text{-NMR}$ Forensic Validation:** Sharp peak at $-310\text{ ppm}$ with $^1J_{N-H} = 73.5 \pm 1.0\text{ Hz}$.

### Part III: Performance Matrix & 3-Blank Forensic Witness
* **Faradaic Efficiency ($FE_{NH3}$):** $\ge 15.0\%$ baseline existence threshold.
* **3-Blank Forensic Witness:**
  1. *Minus-Catalyst:* $0\text{ M } NH_4^+$
  2. *Argon-Atmosphere:* $0\text{ M } NH_4^+$ (verifies ligands do not decompose into ammonia)
  3. *Open-Circuit:* $0\text{ M } NH_4^+$
* **Generation V+1 Mutation Feedback Loop:** Automatic algorithmic guidance (KGS-1 to KGS-4 mutations and Tolman cone angle adjustments).

---

## ⚡ 3. Quickstart: Running the 10-Candidate Test Suite Locally

Clone the repository and run the self-contained validation engine:

```bash
git clone https://github.com/sololys/femos-biomimetic-nitrogenase.git
cd femos-biomimetic-nitrogenase
python3 femos_engine.py
```

### Expected Output:
```text
===============================================================================================
🔬 AETHELGARD MOLECULAR: PROTOKOLL Fe-Mo-S DETERMINISTISK ADMISSIBILITETS-SUITE v3.0
   BIO-UORGANISK ELEKTROKATALYSATOR (N2 -> NH3) MED 3-BLANK WITNESS OG MUTASJONS-LOOP
===============================================================================================
#   | KANDIDAT  | MÅL              | BESLUTN.  | RELÉ   | DIAGNOSE / PROTOKOLL-STATUS
-----------------------------------------------------------------------------------------------
1   | PROTO-01  | Fe=N (Order 2.0) | 🟢 OPEN   |  5.0V | PROTOKOLL_FE_MO_S_FULLT_VERIFISERT_SYNTH
2   | PROTO-02  | Mo=S (Order 1.5) | 🟢 OPEN   |  5.0V | PROTOKOLL_FE_MO_S_FULLT_VERIFISERT_SYNTH
3   | PROTO-03  | Fe=O (Order 2.0) | 🔴 KILL   |  0.0V | AEROBIC_CONTAMINATION (O2=3.5ppm > 1.0ppm)
4   | PROTO-04  | Mo=S (Order 1.0) | 🔴 KILL   |  0.0V | SYSTEM_LATCHED_FAIL_CLOSED_EMERGENCY_SHU
5   | PROTO-05  | Fe=N (Order 1.0) | 🟡 HOLD   |  0.0V | KIE_CAUSALITY_VIOLATION (KIE=2.10 < 5.0)
6   | PROTO-06  | Fe=S (Order 1.0) | 🟠 REJECT |  0.0V | MOSSBAUER_OUT_OF_BOUNDS (δ=0.58 mm/s)
    ↳ 🧬 MUTASJON: KGS-1: Asymmetrisk sigma-injeksjon (Bytt ekvatorialt fosfin med alkyl-NHC)
7   | PROTO-07  | Fe=N (Order 1.0) | 🟡 HOLD   |  0.0V | NMR_ISOTOPIC_INTEGRITY_FAIL (δ=-240.0 ppm)
8   | PROTO-08  | Fe=H (Order 1.0) | 🔴 KILL   |  0.0V | FE_NH3_BELOW_EXISTENCE_THRESHOLD (FE=8.5%)
9   | PROTO-09  | Mo=S (Order 1.0) | 🟡 HOLD   |  0.0V | BLANK_CONTAMINATION_DETECTED (Ar=0.005M)
10  | PROTO-10  | Fe=N (Order 2.0) | 🟢 OPEN   |  5.0V | PROTOKOLL_FE_MO_S_FULLT_VERIFISERT_SYNTH
    ↳ 🧬 MUTASJON: HYSTERESE-VARSEL: Lav TOF -> Øk Tolman kjeglevinkel (θ_cone)
-----------------------------------------------------------------------------------------------
🔒 PROTOKOLL REVISJONSKJEDE (SHA-256): 100% INTAKT & FORSEGLET ✅
===============================================================================================
✅ PROTOKOLL Fe-Mo-S VALIDERINGS-SUITE: ALLE 10 TESTBANER FULLT VERIFISERT
===============================================================================================
```

---

## 🤝 4. Dialogue with UiO, SINTEF & Industrial Partners

This technical framework is open for academic collaboration and pilot benchmarking. Key questions for feasibility projects:
1. Benchmark against existing in situ spectroelectrochemical cells (UiO/SINTEF laboratories).
2. Establish standardized automated WORM witness logs for catalyst reproducibility and European Green Deal compliance.
3. Transition from benchtop simulation to closed-loop experimental automation.

---

## 📜 License & Citation

Licensed under the **MIT License**.

When referencing this work in academic or technical publications, please cite:
> **Torjusen, M. E.** (2026). *Fe-Mo-S Biomimetic Nitrogenase & Deterministic Electrocatalytic Validation Architecture*. ReismannPoint Systems AS // Kreativ Systems. ORCID: [0009-0006-0431-6637](https://orcid.org/0009-0006-0431-6637).
