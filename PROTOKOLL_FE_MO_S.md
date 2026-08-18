# 📜 PROTOKOLL Fe-Mo-S: Admissibel Arkitektur og Elektrokatalytisk Validering

* **Utstedt av:** `Fe-Mo-S (Deterministisk Eksekveringskjerne / Aethelgard Molecular)`
* **Forfatter:** Marius Egerhei Torjusen (ORCID: [0009-0006-0431-6637](https://orcid.org/0009-0006-0431-6637))
* **Domene:** Anaerob bio-uorganisk syntese og elektrokjemisk nitrogenfiksering ($N_2 \to NH_3$)
* **Sikkerhetsstatus:** Fail-Closed (Kandidater som ikke møter invariante kriterier elimineres)
* **Dokument-ID:** `PROTOKOLL-FE-MO-S-VALIDERING-2026-v1.0`

---

## 🔬 DEL I: Kjemisk Arkitektur og Strukturell Integritet

Den syntetiske genereringen av tripodale $\text{MoFe}_3\text{S}_4$-kjerner (f.eks. modifiserte cubaner $[ \text{MoFe}_3\text{S}_4 ]^{3+}$) representerer systemets maskinvare. Denne må etableres under et absolutt anaerobt regime ($O_2 < 1\text{ ppm}$, $H_2O < 1\text{ ppm}$) for å forhindre fatal dannelse av Fe-O-Fe okso-broer.

### 1.1 Invariant Støkiometrisk Kontroll
Den tripodale liganden (f.eks. $\text{HC}(\text{SiMe}_2\text{PPh}_2)_3$ eller modifiserte fosfin-tioetere) utgjør det romlige ankeret (den topologiske porten). Liganden tvinger frem en asymmetrisk binding til Mo-siten, noe som etterlater Fe-sitene i en pseudo-tetraedrisk, reaktiv geometri.

* **Verifikasjon:** Metall-til-svovel og metall-til-ligand forhold SKAL overvåkes via ICP-OES og elementæranalyse.
* **Toleransegrense:** $\le \pm 2.5\%$ avvik. Større avvik trigges som en strukturell `KILL`.

### 1.2 Valideringskriterier for Strukturell Integritet (Arkitektens Nullpunkt)
Før systemet i det hele tatt påføres spenning, må den elektroniske arkitekturen valideres spektroskopisk for å bekrefte at spinn- og oksidasjonstilstand er korrekt konfigurert for d-elektrondonasjon ($\pi$-backbonding) til $N_2$.

* **Mössbauer-Isotopskift ($\delta$) Target (ved 80 K):**
  * $\text{Fe}^{\text{II}}\text{-site}$ (høyspinn): $\delta = 0.45 \pm 0.03\text{ mm/s}$ (Kvadrumpolsplitting $\Delta E_Q = 2.10 \pm 0.15\text{ mm/s}$).
  * $\text{Fe}^{\text{III}}\text{-site}$ (høyspinn): $\delta = 0.28 \pm 0.03\text{ mm/s}$ (Kvadrumpolsplitting $\Delta E_Q = 0.85 \pm 0.10\text{ mm/s}$).
* **Termodynamisk Kjøretøysvindu (Cathodic Potential):**
  * For å initiere den første Proton-Koblede Elektronoverføringen (PCET) kreves det at $E_{\text{cat}}$ ligger presist i vinduet **$-1.45\text{ V}$ til $-1.65\text{ V}$ vs. $\text{Fc/Fc}^+$** (i THF/THF-d8).
  * **Gate-regel:** Et klyngedesign som krever et potensial mer negativt enn $-1.65\text{ V}$ avvises umiddelbart pga. garantert dominans av parasittisk hydrogenutvikling (HER).

---

## ⚡ DEL II: KIE-Protokoll og Spektrale Signaturer (Kausalitetens Speilbrudd)

For å oppfylle AXIOM-prinsippet om "handling før irreversibilitet", må vi bevise (*Witness*) at gassens transformasjon faktisk driver elektrokjemien.

### 2.1 Fullstendig H/D KIE-Protokoll (Veto-Gate)
Ingen designendring tillates før kausalitet er bevist. Systemet må bevise at PCET er det sanne hastighetsbestemmende steget (RDS).
* **Metodikk:** Utfør Syklisk Voltammetri (CV) og Controlled Potential Electrolysis (CPE) ved det fastsatte $E_{\text{cat}}$ med identiske konsentrasjoner av en svak syre og dens deutererte analog (f.eks. $[\text{LutH}]^+$ vs. $[\text{LutD}]^+$).
* **Geometrisk Constraint ($K_{\text{KIE}}$):**
  $$\text{KIE} = \frac{k_H}{k_D} \ge 5.0$$
* **Aksjon:** Verdier under 5.0 forkastes som diffusjonsstøy eller frakoblet elektronoverføring. Fører umiddelbart til `HOLD/KILL`.

### 2.2 Spektral Signatur for $N_2$-Aktivering (in situ IR/Raman)
Dette er *operando* Spektral-Gating. Vi overvåker vibrasjonelle overganger under påført potensial og isotop-substitusjon for å identifisere reaksjonsintermediater.
* **End-on $^{14}N_2$ (Kandidattilstand):**
  * $^{14}N_2$: $\nu(N\equiv N)$ forventes ved $\sim 1980\text{ cm}^{-1}$.
  * $^{15}N_2$: Obligatorisk isotopskift ($\Delta\nu \approx -65\text{ cm}^{-1}$) til $\sim 1915\text{ cm}^{-1}$.
* **Diazenido $\text{Fe-N=NH}$ (Etter 1. PCET-event):**
  * $^{14}N_2$: $\nu(N=N)$ faller til $\sim 1550\text{ cm}^{-1}$ grunnet svekket trippelbinding.
  * $^{15}N_2$: Tydelig skift til $\sim 1490\text{ cm}^{-1}$. *(Dette er signaturkravet for tillatt passering til produkt)*.

### 2.3 Obligatorisk $^{15}N$-NMR Validering (Anti-Selvbedrag)
Målt ammoniakk i elektrolytten er verdiløs hvis den stammer fra ligand-degradering eller atmosfærisk aminkontaminasjon.
* **Prosedyre:** Syreekstraksjon av elektrolytten etter CPE utført med $^{15}N_2$.
* **Signaturkrav:** En skarp kvintett (eller bred triplett) i $^{15}N\text{-NMR}$-spekteret ved **$-310\text{ ppm}$** (referert til $\text{CH}_3\text{NO}_2$).
* **Koblingskonstant:** Krevd $^1J_{N-H} = 73.5 \pm 1.0\text{ Hz}$.
* **Veto:** Uten dette signalet blir reaksjonen **ikke autorisert**.

---

## 📊 DEL III: Ytelsesmatrise og Data-drevet Feedback-Loop

Katalysatorens fysiske konsekvens kvantifiseres strengt mot termodynamiske kostnader. Empirisk gjetning er forbudt; systemet bygger seg selv ut av sine feilsignaturer.

### 3.1 Kvantifisering og Admissibel Ytelse (Faradaic Efficiency)
* **Kvantifiseringsmetode:** Primært Indofenolblå-metoden (UV-Vis absorpsjon ved 630 nm) for $NH_3$. Uavhengig sekundærverifikasjon via Ion Chromatography (IC) for total $NH_4^+$ og eventuell $N_2H_4$ (hydrazin).
* **Gate 1 (Eksistensrett):** $\text{FE}_{NH3} \ge 15.0\%$ ved operasjonelt potensial. Lavere verdi indikerer massiv HER-dominans (`KILL`).
* **Gate 2 (Prestasjonens Alkemiske Vekt):** Senere generasjoner må oppnå $\text{FE}_{NH3} \ge 40.0\%$ ved et overpotensial $\eta \le 250\text{ mV}$ for å godkjennes.

### 3.2 Analytiske Betingelser for Blankforsøk (E-TOR / Forensic Witness)
Tre absolutte E-TOR (Forensic Witness) "blanks" kreves for å opprettholde epistemisk konsistens:
1. **Minus-Katalysator:** CPE med kun elektrode, løsemiddel, støtteelektrolytt, syre og $N_2$. **Krav:** $0\text{ M } NH_4^+$.
2. **Argon-Atmosfære:** Komplett system, spylt utelukkende med Ar. **Krav:** $0\text{ M } NH_4^+$ (beviser at ligander ikke dekomponerer).
3. **Open Circuit:** Komplett system med $N_2$, uten potensial. **Krav:** $0\text{ M } NH_4^+$.

### 3.3 Data-drevet Feedback-Loop (Generasjon V+1: Kryptisk Geometri)
Mössbauer ($\delta$) og elektrokjemiske data danner en rigid algoritme for strukturell mutasjon. Vi anerkjenner at $\text{Turn Over Frequency (TOF)} \propto e^{-\Delta G^\ddagger / RT}$.

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                 ALGORITMISK MUTASJONSMATRISE (GENERASJON V+1)               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  TERSKEL 1 (Det Elektroniske Sluket): δ > 0.55 mm/s                         │
│  • Diagnose: Kritisk elektronfattig Fe-kjerne.                              │
│  • Aksjon (KGS-1): Asymmetrisk σ-injeksjon. Bytt et ekvatorialt fosfin-ben   │
│    med en sterk σ-donerende alkyl-NHC.                                      │
│                                                                             │
│  TERSKEL 2 (Det Marginale Underskuddet): 0.48 < δ ≤ 0.55 mm/s               │
│  • Diagnose: Sub-optimal π-donasjon; overspenningen for PCET er for høy.     │
│  • Aksjon (KGS-2): Perifer donor-induksjon. Introduser moderat donerende     │
│    grupper (f.eks. -OMe) på aryl-ringene for å heve HOMO.                   │
│                                                                             │
│  TERSKEL 3 (Det Marginale Overskuddet): 0.40 ≤ δ < 0.42 mm/s                │
│  • Diagnose: Kjerne for elektronrik. N₂ bindes for hardt; fare for HER.     │
│  • Aksjon (KGS-3): Apikal π-filtrering. Introduser moderat elektron-        │
│    trekkende grupper (f.eks. -CF₃) på den apikale liganden.                 │
│                                                                             │
│  TERSKEL 4 (Den Kvelte Kjernen): δ < 0.40 mm/s                              │
│  • Diagnose: Ekstrem over-reduksjon, fare for klyngedissosiasjon.           │
│  • Aksjon (KGS-4): Tripodal π-tapping. Bytt en chelaterende arm med en      │
│    sterk π-akseptor (f.eks. fosfitt) for drenering av elektrontetthet.      │
│                                                                             │
│  HYSTERESE (Product Inhibition):                                            │
│  • Hvis NH₃ bekreftes men TOF er lav, er klyngen overstabilisert.           │
│  • Aksjon: Øk ligandens koniske vinkel (θ_cone) for å sterisk utstøte NH₃.  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

> **[SLUTT PÅ PROTOKOLL]**  
> *Ingen gjetning tillates. Avvik dikterer form. Form dikterer overlevelse.*
