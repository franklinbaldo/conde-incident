# OKF 🐢/🐙 · 2026-11-12 operational 528 correction

- Base main after #75 #76 #79 #80 #81 #83; use source PR #14 HEAD 48ae4fd70fabe9bfc910a12c6a29916c2a088015.
- Copied current operational TypeScript constants, Python-export source and
  standalone Python script; new provenance test from Tartaruga, dedicated CI.
- Source 528 literal from one secondary source; Git SHA preserved by #83.
- Removes unsupported 528 RAAN=284.1520 from active source vector; 527/529
  old vectors are hypotheses and not primary observations.
- Does not claim authenticated NORAD sensor data, calibrated drag, or impact.
- Review retrospectively by Gavião; other custody modules of PR #14 remain.
