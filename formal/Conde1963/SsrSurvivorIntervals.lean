import Lean

/-!
C241-L18: conditional arithmetic on NASA SSR printed orbital periods.

The original facsimiles are July 31 (NTRS 19630012290), November 30
(NTRS 19640002493), and December 31 (NTRS 19640005618) 1963.
These are *published table values* compiled from a shared tracking system.
Report reference dates are not individual instrument measurement epochs.

The December 1963 C (529) cell has a documented discrepancy:
C227 transcribed 89.6 min; independent review of the current facsimile
reads 89.2 min, now reconciled in C241-L18 on the source facsimile.
The older proofs keep their conservative bounds for compatibility. The
new source-locked result below uses only the reconciled printed interval.
No statement here reconstructs a physical orbit.

Integer units are hundredths of a minute; all proofs are conditional
on the assumed nearest-0.1-minute editorial rounding, not instrument sigma.
-/

namespace Conde1963.SsrSurvivorIntervals

/-- July 1963 B 93.6 vs October 1963 B 92.4, from printed tables. -/
theorem b_july_to_october_published_difference
    (july oct : Int)
    (hj0 : 9355 ≤ july) (hj1 : july ≤ 9365)
    (ho0 : 9235 ≤ oct) (ho1 : oct ≤ 9245) :
    110 ≤ july - oct ∧ july - oct ≤ 130 := by
  omega

/-- Legacy broad bound for C (529): includes both historical transcriptions. -/
theorem c_post_b_november_to_december_published_difference
    (nov dec : Int)
    (hn0 : 9215 ≤ nov) (hn1 : nov ≤ 9225)
    (hd0 : 8915 ≤ dec) (hd1 : dec ≤ 8965) :
    250 ≤ nov - dec ∧ nov - dec ≤ 310 := by
  omega

/-- November-to-December A (527) is unchanged to one printed decimal. -/
theorem a_post_b_november_to_december_published_difference
    (nov dec : Int)
    (hn0 : 9455 ≤ nov) (hn1 : nov ≤ 9465)
    (hd0 : 9455 ≤ dec) (hd1 : dec ≤ 9465) :
    -10 ≤ nov - dec ∧ nov - dec ≤ 10 := by
  omega

/--
Nontrivial *differential* between two control objects survives the 529
transcription conflict. No inference about physical drag is made unless
calibrated epochs, reference frame, ballistic parameters and errors
bridge the reports to states.
-/
theorem post_b_529_change_exceeds_527_change_in_printed_tables
    (nC dC nA dA : Int)
    (hnC0 : 9215 ≤ nC) (hnC1 : nC ≤ 9225)
    (hdC0 : 8915 ≤ dC) (hdC1 : dC ≤ 8965)
    (hnA0 : 9455 ≤ nA) (hnA1 : nA ≤ 9465)
    (hdA0 : 9455 ≤ dA) (hdA1 : dA ≤ 9465) :
    240 ≤ (nC - dC) - (nA - dA) ∧
    (nC - dC) - (nA - dA) ≤ 320 := by
  omega

/-- Source-locked C241-L18: once the 31 Dec 3C printed cell is read as
    89.2 min, and assuming nearest-tenth editorial rounding for 529 and 527,
    the differential *printed* change lies in [2.80,3.20] min.
    This is not an observation of drag, instrument epoch or 528 decay. -/
theorem post_b_529_reconciled_printed_gap_over_527
    (nC dC nA dA : Int)
    (hnC0 : 9215 ≤ nC) (hnC1 : nC ≤ 9225)
    (hdC0 : 8915 ≤ dC) (hdC1 : dC ≤ 8925)
    (hnA0 : 9455 ≤ nA) (hnA1 : nA ≤ 9465)
    (hdA0 : 9455 ≤ dA) (hdA1 : dA ≤ 9465) :
    280 ≤ (nC - dC) - (nA - dA) ∧
    (nC - dC) - (nA - dA) ≤ 320 := by
  omega

end Conde1963.SsrSurvivorIntervals
