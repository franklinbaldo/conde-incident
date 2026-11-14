import Lean

/-!
A range monotonicity certificate for the G59 WGS84 line-of-sight veto.

Coordinates here are **synthetic integer samples in normalized ellipsoid
units**. A point is inside the reference unit ellipsoid when its squared
normalized radius is < 1. A ray is blocked if ANY intervening sample is
inside, even when the endpoint has re-emerged outside the solid Earth.

The general implication is independent of the choice of ray, sampling rate,
or Earth constants. It is not a proof that discrete sampling catches every
continuous intersection; the numerical G59 implementation evaluates the
continuous quadratic minimum. No 1963 film, site survey or NORAD 528 orbit
is inferred from this theorem.
-/

namespace Conde1963.OpticalRayVisibility

structure Point where
  x : Int
  y : Int
  z : Int
  deriving Repr, DecidableEq

def rayPoint (station direction : Point) (distance : Nat) : Point :=
  ⟨station.x + (distance : Int) * direction.x,
   station.y + (distance : Int) * direction.y,
   station.z + (distance : Int) * direction.z⟩

def insideUnitEllipsoid (p : Point) : Prop :=
  p.x*p.x + p.y*p.y + p.z*p.z < 1

def occultedThrough (station direction : Point) (distance : Nat) : Prop :=
  ∃ t : Nat, t ≤ distance ∧ insideUnitEllipsoid (rayPoint station direction t)

/-- A ray cannot regain direct optical visibility by continuing farther beyond
an already intersected opaque body. The check must cover the whole *segment*,
not just the candidate's endpoint. -/
theorem first_earth_entry_excludes_all_larger_ranges
    (station direction : Point) (near far : Nat)
    (hEntry : occultedThrough station direction near)
    (hOrder : near ≤ far) :
    occultedThrough station direction far := by
  rcases hEntry with ⟨t, ht, hInside⟩
  exact ⟨t, Nat.le_trans ht hOrder, hInside⟩

/-- Counterexample to testing station and satellite endpoints only:
both are outside the unit ellipsoid while their joining ray crosses it.
The numbers are synthetic, NOT historical coordinates. -/
theorem endpoints_outside_do_not_imply_clear_ray :
    let s : Point := ⟨2, 0, 0⟩
    let d : Point := ⟨-1, 0, 0⟩
    ¬ insideUnitEllipsoid s ∧
    ¬ insideUnitEllipsoid (rayPoint s d 4) ∧
    occultedThrough s d 4 := by
  dsimp
  refine ⟨by simp [insideUnitEllipsoid], by simp [insideUnitEllipsoid, rayPoint], ?_⟩
  exact ⟨2, by decide, by simp [insideUnitEllipsoid, rayPoint]⟩

end Conde1963.OpticalRayVisibility
