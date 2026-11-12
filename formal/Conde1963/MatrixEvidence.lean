import Conde1963.DocumentaryDay

/-!
# Typed identity AND explicit uncertainty of all 241 matrix occurrences

No row directly establishes a physical decay day, hour, location or impact.
C131/C197 refer to ONE historical catalogue publication. Only the
DOCUMENTARY statement of a catalogued date is proven from the source.
C01 preserves the radio report as a report, not an observed crater.

All other rows explicitly say "individual uncertainty not yet assessed
in this formal transfer", not "false" or "unverified evidence".
No documentary row in this registry is a hard physical predicate.
-/

set_option maxRecDepth 4096

namespace Conde1963

inductive RowPhysicalRole where
  | contextOnly
  | nasaReportedDecayDay
  deriving Repr, DecidableEq

inductive EpistemicUncertainty where
  | requiresIndividualAssessment
  | reportExistsPhysicalOccurrenceUnverified
  | reportedCatalogueDayActualDayUnknown
  deriving Repr, DecidableEq

structure MatrixEvidenceRef where
  labelNumber : Nat
  occurrence : Nat
  matrixLine : Nat
  role : RowPhysicalRole
  uncertainty : EpistemicUncertainty
  deriving Repr, DecidableEq

def evidenceMatrixRows : List MatrixEvidenceRef := [
  ⟨1, 1, 19, .contextOnly, .reportExistsPhysicalOccurrenceUnverified⟩,
  ⟨2, 1, 20, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨3, 1, 21, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨4, 1, 22, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨5, 1, 23, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨6, 1, 24, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨7, 1, 25, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨8, 1, 26, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨9, 1, 27, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨10, 1, 28, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨11, 1, 29, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨12, 1, 30, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨13, 1, 31, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨14, 1, 32, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨15, 1, 33, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨16, 1, 34, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨17, 1, 36, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨18, 1, 37, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨19, 1, 38, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨20, 1, 39, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨21, 1, 40, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨22, 1, 41, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨23, 1, 42, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨24, 1, 117, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨25, 1, 118, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨26, 1, 119, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨27, 1, 120, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨28, 1, 121, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨29, 1, 122, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨30, 1, 123, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨31, 1, 124, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨32, 1, 125, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨33, 1, 138, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨34, 1, 139, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨35, 1, 145, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨36, 1, 146, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨37, 1, 147, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨38, 1, 148, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨39, 1, 149, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨40, 1, 150, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨41, 1, 151, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨42, 1, 152, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨43, 1, 153, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨44, 1, 164, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨45, 1, 165, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨46, 1, 166, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨44, 2, 175, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨45, 2, 176, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨46, 2, 177, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨47, 1, 178, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨48, 1, 179, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨49, 1, 180, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨50, 1, 181, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨51, 1, 182, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨52, 1, 183, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨53, 1, 187, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨54, 1, 194, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨55, 1, 195, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨56, 1, 196, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨57, 1, 197, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨58, 1, 198, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨59, 1, 199, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨60, 1, 200, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨61, 1, 201, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨62, 1, 202, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨63, 1, 203, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨64, 1, 228, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨65, 1, 229, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨66, 1, 230, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨67, 1, 231, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨68, 1, 232, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨69, 1, 245, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨70, 1, 246, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨71, 1, 247, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨72, 1, 248, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨73, 1, 261, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨74, 1, 262, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨75, 1, 263, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨76, 1, 264, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨77, 1, 277, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨78, 1, 278, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨79, 1, 279, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨80, 1, 280, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨81, 1, 281, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨82, 1, 282, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨83, 1, 283, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨84, 1, 293, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨85, 1, 294, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨86, 1, 295, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨87, 1, 296, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨88, 1, 297, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨89, 1, 298, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨90, 1, 311, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨91, 1, 312, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨92, 1, 313, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨93, 1, 314, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨94, 1, 315, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨95, 1, 316, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨96, 1, 317, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨97, 1, 346, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨98, 1, 347, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨99, 1, 348, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨100, 1, 349, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨101, 1, 350, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨102, 1, 377, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨103, 1, 378, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨104, 1, 379, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨105, 1, 380, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨106, 1, 381, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨107, 1, 382, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨108, 1, 383, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨109, 1, 384, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨110, 1, 385, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨111, 1, 418, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨112, 1, 419, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨113, 1, 420, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨114, 1, 421, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨115, 1, 422, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨116, 1, 423, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨117, 1, 424, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨118, 1, 456, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨119, 1, 457, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨120, 1, 458, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨121, 1, 459, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨122, 1, 460, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨123, 1, 482, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨124, 1, 483, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨125, 1, 484, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨126, 1, 485, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨127, 1, 486, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨128, 1, 487, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨129, 1, 488, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨130, 1, 489, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨131, 1, 502, .nasaReportedDecayDay, .reportedCatalogueDayActualDayUnknown⟩,
  ⟨132, 1, 503, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨133, 1, 504, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨134, 1, 505, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨135, 1, 506, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨136, 1, 507, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨137, 1, 508, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨138, 1, 509, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨139, 1, 522, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨140, 1, 523, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨141, 1, 524, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨142, 1, 525, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨143, 1, 526, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨144, 1, 541, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨145, 1, 542, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨146, 1, 543, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨147, 1, 544, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨148, 1, 545, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨149, 1, 604, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨150, 1, 605, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨151, 1, 606, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨152, 1, 607, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨153, 1, 608, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨154, 1, 609, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨155, 1, 610, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨156, 1, 668, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨157, 1, 669, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨158, 1, 670, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨159, 1, 671, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨160, 1, 672, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨161, 1, 673, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨162, 1, 702, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨163, 1, 703, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨164, 1, 704, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨165, 1, 705, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨166, 1, 706, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨167, 1, 735, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨168, 1, 736, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨169, 1, 737, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨170, 1, 738, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨171, 1, 739, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨172, 1, 783, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨173, 1, 784, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨174, 1, 785, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨175, 1, 786, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨176, 1, 787, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨177, 1, 788, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨178, 1, 789, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨179, 1, 839, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨180, 1, 840, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨181, 1, 841, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨182, 1, 842, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨183, 1, 843, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨184, 1, 844, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨185, 1, 845, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨186, 1, 846, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨187, 1, 847, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨188, 1, 869, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨189, 1, 870, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨190, 1, 871, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨191, 1, 872, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨192, 1, 873, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨193, 1, 874, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨194, 1, 875, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨195, 1, 876, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨196, 1, 877, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨197, 1, 905, .nasaReportedDecayDay, .reportedCatalogueDayActualDayUnknown⟩,
  ⟨198, 1, 906, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨199, 1, 907, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨200, 1, 908, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨201, 1, 909, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨202, 1, 910, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨203, 1, 925, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨204, 1, 926, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨205, 1, 927, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨206, 1, 928, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨207, 1, 929, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨208, 1, 930, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨209, 1, 931, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨210, 1, 932, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨211, 1, 933, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨212, 1, 948, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨213, 1, 949, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨214, 1, 950, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨215, 1, 951, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨216, 1, 952, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨217, 1, 953, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨218, 1, 954, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨219, 1, 975, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨220, 1, 976, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨221, 1, 977, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨222, 1, 978, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨223, 1, 979, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨224, 1, 980, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨225, 1, 981, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨226, 1, 982, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨227, 1, 1006, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨228, 1, 1007, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨229, 1, 1008, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨230, 1, 1009, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨231, 1, 1010, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨232, 1, 1031, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨233, 1, 1032, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨234, 1, 1033, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨235, 1, 1034, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨236, 1, 1035, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨237, 1, 1036, .contextOnly, .requiresIndividualAssessment⟩,
  ⟨238, 1, 1037, .contextOnly, .requiresIndividualAssessment⟩,
]

/-- Membership in a catalogue of documentary claims imposes NO physical
    restriction until separately reviewed and explicitly admitted with
    a calibrated observational error model. -/
def acceptedMatrixPredicate
    (_row : MatrixEvidenceRef) (_candidate : ReentryCandidate) : Prop :=
  True

def AllMatrixEvidence (candidate : ReentryCandidate) : Prop :=
  ∀ row, row ∈ evidenceMatrixRows → acceptedMatrixPredicate row candidate

theorem evidence_matrix_row_count : evidenceMatrixRows.length = 241 := by decide

theorem nasa_matrix_rows_explicitly_mark_uncertainty :
    (⟨131, 1, 502, .nasaReportedDecayDay,
       .reportedCatalogueDayActualDayUnknown⟩ : MatrixEvidenceRef) ∈ evidenceMatrixRows ∧
    (⟨197, 1, 905, .nasaReportedDecayDay,
       .reportedCatalogueDayActualDayUnknown⟩ : MatrixEvidenceRef) ∈ evidenceMatrixRows := by
  decide

theorem tupi_report_is_not_ground_observation :
    (⟨1, 1, 19, .contextOnly,
       .reportExistsPhysicalOccurrenceUnverified⟩ : MatrixEvidenceRef) ∈ evidenceMatrixRows := by
  decide

theorem every_row_is_nonphysical_without_additional_premises
    (candidate : ReentryCandidate) :
    AllMatrixEvidence candidate := by
  intro row _
  trivial

/-- Even an illustrated off-day state survives documentary indexing.
    This is an epistemic countermodel, not a historical prediction. -/
theorem matrix_does_not_force_nasa_reported_day :
    AllMatrixEvidence inventedOffDayExample ∧
    ¬ PhysicalDayMatchesCatalogue inventedOffDayExample := by
  exact ⟨every_row_is_nonphysical_without_additional_premises _, by decide⟩

theorem full_matrix_does_not_identify_region :
    ¬ UniquelyIdentifiesRegion AllMatrixEvidence (fun _ => True) := by
  apply two_admissible_regions_preclude_unique
    AllMatrixEvidence (fun _ => True) condeCandidate anotherCandidate
  · exact ⟨every_row_is_nonphysical_without_additional_premises _, True.intro⟩
  · exact ⟨every_row_is_nonphysical_without_additional_premises _, True.intro⟩
  · exact date_alone_does_not_identify_place.2.2

end Conde1963
