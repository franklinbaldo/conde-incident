import Conde1963.Documentary

/-!
Generated from Abelha's declared-dependence/v1 companion and the pinned
matrix snapshot. These are real documentary chains attached to existing
formal contracts, not new tracking observations, sensors or orbital bounds.
No hand editing: formal/scripts/compile_contract_lineage.py --check.
-/

namespace Conde1963

structure DeclaredDocumentEdge where
  sourceId : String
  targetId : String
  relation : String
  deriving Repr, BEq

structure DeclaredDocumentAncestry where
  ancestorSourceId : String
  edges : Array DeclaredDocumentEdge
  deriving Repr

structure ContractDocumentaryLineage where
  contractId : String
  contractStatus : String
  matrixRef : MatrixRef
  sourceId : String
  familyId : String
  workId : String
  ancestry : Array DeclaredDocumentAncestry
  deriving Repr

def contractDocumentaryLineages : Array ContractDocumentaryLineage := #[
  { contractId := "C179_ORBITAL_GRAPH", contractStatus := "CANDIDATE_NOT_ACTIVATED", matrixRef := { snapshot := "a7978c3a75a153b16ab70118a92c434bba674cb7", label := 179, variant := 1 }, sourceId := "AFSPC_MIRROR_528", familyId := "NORAD_NASA_TRACKING", workId := "AFSPC_TLE_528_19631027", ancestry := #[] },
  { contractId := "C179_ORBITAL_GRAPH", contractStatus := "CANDIDATE_NOT_ACTIVATED", matrixRef := { snapshot := "a7978c3a75a153b16ab70118a92c434bba674cb7", label := 197, variant := 1 }, sourceId := "NASA_SSR_19631115", familyId := "NORAD_NASA_TRACKING", workId := "NASA_SSR_VOL3_22", ancestry := #[] },
  { contractId := "C179_C151_BRIDGE", contractStatus := "DERIVED_ONLY_NO_CONDE_TRANSFER", matrixRef := { snapshot := "a7978c3a75a153b16ab70118a92c434bba674cb7", label := 179, variant := 1 }, sourceId := "AFSPC_MIRROR_528", familyId := "NORAD_NASA_TRACKING", workId := "AFSPC_TLE_528_19631027", ancestry := #[] },
  { contractId := "C179_C151_BRIDGE", contractStatus := "DERIVED_ONLY_NO_CONDE_TRANSFER", matrixRef := { snapshot := "a7978c3a75a153b16ab70118a92c434bba674cb7", label := 151, variant := 1 }, sourceId := "NOAA_IGRA_RECIFE_1963", familyId := "NOAA_IGRA_RECIFE", workId := "IGRA_BRM00082900_PROFILE_19631108", ancestry := #[] },
  { contractId := "C197_DOCUMENTARY", contractStatus := "DOCUMENTARY_DAY_ONLY", matrixRef := { snapshot := "a7978c3a75a153b16ab70118a92c434bba674cb7", label := 131, variant := 1 }, sourceId := "NASA_SSR_19631115", familyId := "NORAD_NASA_TRACKING", workId := "NASA_SSR_VOL3_22", ancestry := #[] },
  { contractId := "C197_DOCUMENTARY", contractStatus := "DOCUMENTARY_DAY_ONLY", matrixRef := { snapshot := "a7978c3a75a153b16ab70118a92c434bba674cb7", label := 197, variant := 1 }, sourceId := "NASA_SSR_19631115", familyId := "NORAD_NASA_TRACKING", workId := "NASA_SSR_VOL3_22", ancestry := #[] },
  { contractId := "C197_DOCUMENTARY", contractStatus := "DOCUMENTARY_DAY_ONLY", matrixRef := { snapshot := "a7978c3a75a153b16ab70118a92c434bba674cb7", label := 198, variant := 1 }, sourceId := "NTRS_19640001198", familyId := "NORAD_NASA_TRACKING", workId := "NASA_SSR_VOL3_22", ancestry := #[{ ancestorSourceId := "NASA_SSR_19631115", edges := #[{ sourceId := "NTRS_19640001198", targetId := "NASA_SSR_19631115", relation := "catalogue_of_same_work" }] }] },
  { contractId := "C197_DOCUMENTARY", contractStatus := "DOCUMENTARY_DAY_ONLY", matrixRef := { snapshot := "a7978c3a75a153b16ab70118a92c434bba674cb7", label := 200, variant := 1 }, sourceId := "NASA_SSR_19631115", familyId := "NORAD_NASA_TRACKING", workId := "NASA_SSR_VOL3_22", ancestry := #[] }
]

end Conde1963
