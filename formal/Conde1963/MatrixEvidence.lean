import Conde1963.DocumentaryDay

/-!
# Complete C01-C238 matrix identity, NOT a model of 241 measured orbits

Every actual markdown evidence row has a unique tuple (numeric ID,
occurrence, pinned line). C44-C46 legitimately occur twice. Its documentary
text, status and lineage remain at the pinned matrix citation. Lean does not
infer authenticity from this registry. Only C131/C197 encode an accepted
*conditional* NASA-reported decay-day filter; other rows have not yet been
justified as terminal-state restrictions. No ground impact is asserted.
-/

namespace Conde1963

inductive RowPhysicalRole where
  | contextOnly
  | nasaReportedDecayDay
  deriving Repr, DecidableEq

structure MatrixEvidenceRef where
  labelNumber : Nat
  occurrence : Nat
  matrixLine : Nat
  role : RowPhysicalRole
  deriving Repr, DecidableEq

def evidenceMatrixRows : List MatrixEvidenceRef := [
  ⟨1, 1, 19, .contextOnly⟩,
  ⟨2, 1, 20, .contextOnly⟩,
  ⟨3, 1, 21, .contextOnly⟩,
  ⟨4, 1, 22, .contextOnly⟩,
  ⟨5, 1, 23, .contextOnly⟩,
  ⟨6, 1, 24, .contextOnly⟩,
  ⟨7, 1, 25, .contextOnly⟩,
  ⟨8, 1, 26, .contextOnly⟩,
  ⟨9, 1, 27, .contextOnly⟩,
  ⟨10, 1, 28, .contextOnly⟩,
  ⟨11, 1, 29, .contextOnly⟩,
  ⟨12, 1, 30, .contextOnly⟩,
  ⟨13, 1, 31, .contextOnly⟩,
  ⟨14, 1, 32, .contextOnly⟩,
  ⟨15, 1, 33, .contextOnly⟩,
  ⟨16, 1, 34, .contextOnly⟩,
  ⟨17, 1, 36, .contextOnly⟩,
  ⟨18, 1, 37, .contextOnly⟩,
  ⟨19, 1, 38, .contextOnly⟩,
  ⟨20, 1, 39, .contextOnly⟩,
  ⟨21, 1, 40, .contextOnly⟩,
  ⟨22, 1, 41, .contextOnly⟩,
  ⟨23, 1, 42, .contextOnly⟩,
  ⟨24, 1, 117, .contextOnly⟩,
  ⟨25, 1, 118, .contextOnly⟩,
  ⟨26, 1, 119, .contextOnly⟩,
  ⟨27, 1, 120, .contextOnly⟩,
  ⟨28, 1, 121, .contextOnly⟩,
  ⟨29, 1, 122, .contextOnly⟩,
  ⟨30, 1, 123, .contextOnly⟩,
  ⟨31, 1, 124, .contextOnly⟩,
  ⟨32, 1, 125, .contextOnly⟩,
  ⟨33, 1, 138, .contextOnly⟩,
  ⟨34, 1, 139, .contextOnly⟩,
  ⟨35, 1, 145, .contextOnly⟩,
  ⟨36, 1, 146, .contextOnly⟩,
  ⟨37, 1, 147, .contextOnly⟩,
  ⟨38, 1, 148, .contextOnly⟩,
  ⟨39, 1, 149, .contextOnly⟩,
  ⟨40, 1, 150, .contextOnly⟩,
  ⟨41, 1, 151, .contextOnly⟩,
  ⟨42, 1, 152, .contextOnly⟩,
  ⟨43, 1, 153, .contextOnly⟩,
  ⟨44, 1, 164, .contextOnly⟩,
  ⟨45, 1, 165, .contextOnly⟩,
  ⟨46, 1, 166, .contextOnly⟩,
  ⟨44, 2, 175, .contextOnly⟩,
  ⟨45, 2, 176, .contextOnly⟩,
  ⟨46, 2, 177, .contextOnly⟩,
  ⟨47, 1, 178, .contextOnly⟩,
  ⟨48, 1, 179, .contextOnly⟩,
  ⟨49, 1, 180, .contextOnly⟩,
  ⟨50, 1, 181, .contextOnly⟩,
  ⟨51, 1, 182, .contextOnly⟩,
  ⟨52, 1, 183, .contextOnly⟩,
  ⟨53, 1, 187, .contextOnly⟩,
  ⟨54, 1, 194, .contextOnly⟩,
  ⟨55, 1, 195, .contextOnly⟩,
  ⟨56, 1, 196, .contextOnly⟩,
  ⟨57, 1, 197, .contextOnly⟩,
  ⟨58, 1, 198, .contextOnly⟩,
  ⟨59, 1, 199, .contextOnly⟩,
  ⟨60, 1, 200, .contextOnly⟩,
  ⟨61, 1, 201, .contextOnly⟩,
  ⟨62, 1, 202, .contextOnly⟩,
  ⟨63, 1, 203, .contextOnly⟩,
  ⟨64, 1, 228, .contextOnly⟩,
  ⟨65, 1, 229, .contextOnly⟩,
  ⟨66, 1, 230, .contextOnly⟩,
  ⟨67, 1, 231, .contextOnly⟩,
  ⟨68, 1, 232, .contextOnly⟩,
  ⟨69, 1, 245, .contextOnly⟩,
  ⟨70, 1, 246, .contextOnly⟩,
  ⟨71, 1, 247, .contextOnly⟩,
  ⟨72, 1, 248, .contextOnly⟩,
  ⟨73, 1, 261, .contextOnly⟩,
  ⟨74, 1, 262, .contextOnly⟩,
  ⟨75, 1, 263, .contextOnly⟩,
  ⟨76, 1, 264, .contextOnly⟩,
  ⟨77, 1, 277, .contextOnly⟩,
  ⟨78, 1, 278, .contextOnly⟩,
  ⟨79, 1, 279, .contextOnly⟩,
  ⟨80, 1, 280, .contextOnly⟩,
  ⟨81, 1, 281, .contextOnly⟩,
  ⟨82, 1, 282, .contextOnly⟩,
  ⟨83, 1, 283, .contextOnly⟩,
  ⟨84, 1, 293, .contextOnly⟩,
  ⟨85, 1, 294, .contextOnly⟩,
  ⟨86, 1, 295, .contextOnly⟩,
  ⟨87, 1, 296, .contextOnly⟩,
  ⟨88, 1, 297, .contextOnly⟩,
  ⟨89, 1, 298, .contextOnly⟩,
  ⟨90, 1, 311, .contextOnly⟩,
  ⟨91, 1, 312, .contextOnly⟩,
  ⟨92, 1, 313, .contextOnly⟩,
  ⟨93, 1, 314, .contextOnly⟩,
  ⟨94, 1, 315, .contextOnly⟩,
  ⟨95, 1, 316, .contextOnly⟩,
  ⟨96, 1, 317, .contextOnly⟩,
  ⟨97, 1, 346, .contextOnly⟩,
  ⟨98, 1, 347, .contextOnly⟩,
  ⟨99, 1, 348, .contextOnly⟩,
  ⟨100, 1, 349, .contextOnly⟩,
  ⟨101, 1, 350, .contextOnly⟩,
  ⟨102, 1, 377, .contextOnly⟩,
  ⟨103, 1, 378, .contextOnly⟩,
  ⟨104, 1, 379, .contextOnly⟩,
  ⟨105, 1, 380, .contextOnly⟩,
  ⟨106, 1, 381, .contextOnly⟩,
  ⟨107, 1, 382, .contextOnly⟩,
  ⟨108, 1, 383, .contextOnly⟩,
  ⟨109, 1, 384, .contextOnly⟩,
  ⟨110, 1, 385, .contextOnly⟩,
  ⟨111, 1, 418, .contextOnly⟩,
  ⟨112, 1, 419, .contextOnly⟩,
  ⟨113, 1, 420, .contextOnly⟩,
  ⟨114, 1, 421, .contextOnly⟩,
  ⟨115, 1, 422, .contextOnly⟩,
  ⟨116, 1, 423, .contextOnly⟩,
  ⟨117, 1, 424, .contextOnly⟩,
  ⟨118, 1, 456, .contextOnly⟩,
  ⟨119, 1, 457, .contextOnly⟩,
  ⟨120, 1, 458, .contextOnly⟩,
  ⟨121, 1, 459, .contextOnly⟩,
  ⟨122, 1, 460, .contextOnly⟩,
  ⟨123, 1, 482, .contextOnly⟩,
  ⟨124, 1, 483, .contextOnly⟩,
  ⟨125, 1, 484, .contextOnly⟩,
  ⟨126, 1, 485, .contextOnly⟩,
  ⟨127, 1, 486, .contextOnly⟩,
  ⟨128, 1, 487, .contextOnly⟩,
  ⟨129, 1, 488, .contextOnly⟩,
  ⟨130, 1, 489, .contextOnly⟩,
  ⟨131, 1, 502, .nasaReportedDecayDay⟩,
  ⟨132, 1, 503, .contextOnly⟩,
  ⟨133, 1, 504, .contextOnly⟩,
  ⟨134, 1, 505, .contextOnly⟩,
  ⟨135, 1, 506, .contextOnly⟩,
  ⟨136, 1, 507, .contextOnly⟩,
  ⟨137, 1, 508, .contextOnly⟩,
  ⟨138, 1, 509, .contextOnly⟩,
  ⟨139, 1, 522, .contextOnly⟩,
  ⟨140, 1, 523, .contextOnly⟩,
  ⟨141, 1, 524, .contextOnly⟩,
  ⟨142, 1, 525, .contextOnly⟩,
  ⟨143, 1, 526, .contextOnly⟩,
  ⟨144, 1, 541, .contextOnly⟩,
  ⟨145, 1, 542, .contextOnly⟩,
  ⟨146, 1, 543, .contextOnly⟩,
  ⟨147, 1, 544, .contextOnly⟩,
  ⟨148, 1, 545, .contextOnly⟩,
  ⟨149, 1, 604, .contextOnly⟩,
  ⟨150, 1, 605, .contextOnly⟩,
  ⟨151, 1, 606, .contextOnly⟩,
  ⟨152, 1, 607, .contextOnly⟩,
  ⟨153, 1, 608, .contextOnly⟩,
  ⟨154, 1, 609, .contextOnly⟩,
  ⟨155, 1, 610, .contextOnly⟩,
  ⟨156, 1, 668, .contextOnly⟩,
  ⟨157, 1, 669, .contextOnly⟩,
  ⟨158, 1, 670, .contextOnly⟩,
  ⟨159, 1, 671, .contextOnly⟩,
  ⟨160, 1, 672, .contextOnly⟩,
  ⟨161, 1, 673, .contextOnly⟩,
  ⟨162, 1, 702, .contextOnly⟩,
  ⟨163, 1, 703, .contextOnly⟩,
  ⟨164, 1, 704, .contextOnly⟩,
  ⟨165, 1, 705, .contextOnly⟩,
  ⟨166, 1, 706, .contextOnly⟩,
  ⟨167, 1, 735, .contextOnly⟩,
  ⟨168, 1, 736, .contextOnly⟩,
  ⟨169, 1, 737, .contextOnly⟩,
  ⟨170, 1, 738, .contextOnly⟩,
  ⟨171, 1, 739, .contextOnly⟩,
  ⟨172, 1, 783, .contextOnly⟩,
  ⟨173, 1, 784, .contextOnly⟩,
  ⟨174, 1, 785, .contextOnly⟩,
  ⟨175, 1, 786, .contextOnly⟩,
  ⟨176, 1, 787, .contextOnly⟩,
  ⟨177, 1, 788, .contextOnly⟩,
  ⟨178, 1, 789, .contextOnly⟩,
  ⟨179, 1, 839, .contextOnly⟩,
  ⟨180, 1, 840, .contextOnly⟩,
  ⟨181, 1, 841, .contextOnly⟩,
  ⟨182, 1, 842, .contextOnly⟩,
  ⟨183, 1, 843, .contextOnly⟩,
  ⟨184, 1, 844, .contextOnly⟩,
  ⟨185, 1, 845, .contextOnly⟩,
  ⟨186, 1, 846, .contextOnly⟩,
  ⟨187, 1, 847, .contextOnly⟩,
  ⟨188, 1, 869, .contextOnly⟩,
  ⟨189, 1, 870, .contextOnly⟩,
  ⟨190, 1, 871, .contextOnly⟩,
  ⟨191, 1, 872, .contextOnly⟩,
  ⟨192, 1, 873, .contextOnly⟩,
  ⟨193, 1, 874, .contextOnly⟩,
  ⟨194, 1, 875, .contextOnly⟩,
  ⟨195, 1, 876, .contextOnly⟩,
  ⟨196, 1, 877, .contextOnly⟩,
  ⟨197, 1, 905, .nasaReportedDecayDay⟩,
  ⟨198, 1, 906, .contextOnly⟩,
  ⟨199, 1, 907, .contextOnly⟩,
  ⟨200, 1, 908, .contextOnly⟩,
  ⟨201, 1, 909, .contextOnly⟩,
  ⟨202, 1, 910, .contextOnly⟩,
  ⟨203, 1, 925, .contextOnly⟩,
  ⟨204, 1, 926, .contextOnly⟩,
  ⟨205, 1, 927, .contextOnly⟩,
  ⟨206, 1, 928, .contextOnly⟩,
  ⟨207, 1, 929, .contextOnly⟩,
  ⟨208, 1, 930, .contextOnly⟩,
  ⟨209, 1, 931, .contextOnly⟩,
  ⟨210, 1, 932, .contextOnly⟩,
  ⟨211, 1, 933, .contextOnly⟩,
  ⟨212, 1, 948, .contextOnly⟩,
  ⟨213, 1, 949, .contextOnly⟩,
  ⟨214, 1, 950, .contextOnly⟩,
  ⟨215, 1, 951, .contextOnly⟩,
  ⟨216, 1, 952, .contextOnly⟩,
  ⟨217, 1, 953, .contextOnly⟩,
  ⟨218, 1, 954, .contextOnly⟩,
  ⟨219, 1, 975, .contextOnly⟩,
  ⟨220, 1, 976, .contextOnly⟩,
  ⟨221, 1, 977, .contextOnly⟩,
  ⟨222, 1, 978, .contextOnly⟩,
  ⟨223, 1, 979, .contextOnly⟩,
  ⟨224, 1, 980, .contextOnly⟩,
  ⟨225, 1, 981, .contextOnly⟩,
  ⟨226, 1, 982, .contextOnly⟩,
  ⟨227, 1, 1006, .contextOnly⟩,
  ⟨228, 1, 1007, .contextOnly⟩,
  ⟨229, 1, 1008, .contextOnly⟩,
  ⟨230, 1, 1009, .contextOnly⟩,
  ⟨231, 1, 1010, .contextOnly⟩,
  ⟨232, 1, 1031, .contextOnly⟩,
  ⟨233, 1, 1032, .contextOnly⟩,
  ⟨234, 1, 1033, .contextOnly⟩,
  ⟨235, 1, 1034, .contextOnly⟩,
  ⟨236, 1, 1035, .contextOnly⟩,
  ⟨237, 1, 1036, .contextOnly⟩,
  ⟨238, 1, 1037, .contextOnly⟩,
]

/-- An entry with no independently justified physical mapping constrains
    nothing. The NASA case constrains only the reported decay calendar day
    in a specifically chosen scenario, never a ground-impact date. -/
def acceptedMatrixPredicate
    (row : MatrixEvidenceRef) (candidate : ReentryCandidate) : Prop :=
  match row.role with
  | .contextOnly => True
  | .nasaReportedDecayDay => ReportedDecayDay candidate

/-- Conjunction of all *currently encoded* restrictions, not all possible
    implications of all historical texts. -/
def AllMatrixEvidence (candidate : ReentryCandidate) : Prop :=
  ∀ row, row ∈ evidenceMatrixRows → acceptedMatrixPredicate row candidate

theorem evidence_matrix_row_count : evidenceMatrixRows.length = 241 := by decide

theorem two_primary_nasa_matrix_occurrences :
    (⟨131, 1, 502, .nasaReportedDecayDay⟩ : MatrixEvidenceRef) ∈ evidenceMatrixRows ∧
    (⟨197, 1, 905, .nasaReportedDecayDay⟩ : MatrixEvidenceRef) ∈ evidenceMatrixRows := by
  decide

theorem context_rows_add_no_orbital_information
    (row : MatrixEvidenceRef) (candidate : ReentryCandidate)
    (h : row.role = .contextOnly) :
    acceptedMatrixPredicate row candidate := by
  simp [acceptedMatrixPredicate, h]

/-- 241 indexed occurrences, but only one distinct day filter currently
    accepted. This is a coverage statement, NOT a finding that other
    primary observations are unimportant or false. -/
theorem full_matrix_has_only_nasa_day_filter
    (candidate : ReentryCandidate) :
    AllMatrixEvidence candidate ↔ ReportedDecayDay candidate := by
  constructor
  · intro h
    exact h _ two_primary_nasa_matrix_occurrences.1
  · intro h row _
    cases row.role with
    | contextOnly => trivial
    | nasaReportedDecayDay => exact h

/-- Both illustrative regions remain possible under currently encoded
    restrictions. No claim about an actual 1963 orbit or impact follows. -/
theorem full_matrix_does_not_identify_region :
    ¬ UniquelyIdentifiesRegion AllMatrixEvidence (fun _ => True) := by
  apply two_admissible_regions_preclude_unique
    AllMatrixEvidence (fun _ => True) condeCandidate anotherCandidate
  · exact ⟨(full_matrix_has_only_nasa_day_filter condeCandidate).2 rfl, True.intro⟩
  · exact ⟨(full_matrix_has_only_nasa_day_filter anotherCandidate).2 rfl, True.intro⟩
  · exact date_alone_does_not_identify_place.2.2

end Conde1963
