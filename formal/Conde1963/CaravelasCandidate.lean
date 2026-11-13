import Conde1963.Documentary

/-!
Caravelas NOAA/ISD source G36 is not part of the frozen C001-C238 matrix.
It supplies 72 station-hour rows, not 72 independent sources. This typed
candidate identifies a possible atmospheric input; it does not impose an
inequality on the 528 trajectory or certify a Conde wind observation.
-/

namespace Conde1963

structure ArchivedSurfaceCandidate where
  sourceId : String
  stationUsaf : String
  windowSha256 : String
  observations : Nat
  status : String
  latentParameter : String
  deriving Repr

def caravelas1963Candidate : ArchivedSurfaceCandidate :=
  { sourceId := "MET-ISD-19631107-09-CARAVELAS-01"
    stationUsaf := "834970"
    windowSha256 := "c6926a86150df982d13286285c17a70e4752cb1ce0ffe1d44ae5330be215a000"
    observations := 72
    status := "CONNECTED_PENDING_SPATIOTEMPORAL_CALIBRATION"
    latentParameter := "wind_field_nov_1963_with_altitude_time_and_position" }

-- The matched C151#1 is IGRA Recife context, not a Caravelas measurement.
def caravelasComparisonContext : MatrixRef :=
  { snapshot := "a7978c3a75a153b16ab70118a92c434bba674cb7"
    label := 151, variant := 1 }

end Conde1963
