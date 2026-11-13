import Lean

/-!
C241-L39. GCAT reports S00527 OPS 0180 Mass=306 kg, Agena A00324
Mass=900 kg and DryMass=870 kg, with associated TotMass=1176 kg.
Here these numbers are integer *catalog constants*, in grams.

The algebra below identifies the 30 kg definitional mismatch. It does NOT
prove 30 kg of fuel were spent at an observed epoch. m527 is potentially
a payload+stage composite, so 306 kg must not be assigned directly to the
whole orbital object 527.

All physical-mass inequalities require independently justified premises
about attached components, retained mass, source dates, and inventory.
-/

namespace Conde1963.MassComponent306

def payloadMassGrams : Nat := 306000

def stageWetGrams : Nat := 900000

def stageDryGrams : Nat := 870000

def reportedTotalGrams : Nat := 1176000

/-- The two nominal Mass fields sum to 1206 kg, 30 kg above TotMass. -/
theorem wet_sum_exceeds_reported_total :
    payloadMassGrams + stageWetGrams = reportedTotalGrams + 30000 := by
  decide

/-- Payload Mass plus stage DryMass matches reported TotMass numerically.
Matching numbers does NOT certify matching measurement epochs. -/
theorem dry_sum_equals_reported_total :
    payloadMassGrams + stageDryGrams = reportedTotalGrams := by
  decide

/-- The difference between nominal stage wet and dry catalogue fields is
30 kg; this is not an observed fuel consumption trajectory. -/
theorem stage_mass_field_difference :
    stageDryGrams + 30000 = stageWetGrams := by
  decide

/-- Under a separately documented component-retention model, a composite
cannot weigh LESS than a retained payload that is part of it. -/
theorem composite_contains_retained_payload
    (m527 retainedPayload retainedStage otherAttached : Nat)
    (h : m527 = retainedPayload + retainedStage + otherAttached) :
    retainedPayload ≤ m527 := by
  omega

/-- If initial payload mass truly was 306 kg and all its matter is
accounted either as retained in 527 or separated, this conditional
relation follows. The 'separated' part may belong to 528, 529, X, etc. -/
theorem composite_plus_separated_payload_at_least_306
    (m527 retainedPayload separatedPayload retainedStage otherAttached : Nat)
    (hinventory : retainedPayload + separatedPayload = payloadMassGrams)
    (hcomposite : m527 = retainedPayload + retainedStage + otherAttached) :
    payloadMassGrams ≤ m527 + separatedPayload := by
  dsimp [payloadMassGrams] at *
  omega

end Conde1963.MassComponent306
