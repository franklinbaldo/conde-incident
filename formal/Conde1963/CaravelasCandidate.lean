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
  observedVariable : String
  spatialTarget : String
  spatialTransfer : Option String
  stationPosition1963 : Option String
  instrumentCovariance : Option String
  terminalEpoch528 : Option String
  deriving Repr

def caravelas1963Candidate : ArchivedSurfaceCandidate :=
  { sourceId := "MET-ISD-19631107-09-CARAVELAS-01"
    stationUsaf := "834970"
    windowSha256 := "c6926a86150df982d13286285c17a70e4752cb1ce0ffe1d44ae5330be215a000"
    observations := 72
    status := "CONNECTED_PENDING_SPATIOTEMPORAL_CALIBRATION"
    latentParameter := "wind_field_nov_1963_with_altitude_time_and_position"
    observedVariable := "Caravelas_surface_wind_at_hour_t"
    spatialTarget := "Conde_surface_wind_at_hour_t"
    spatialTransfer := none
    stationPosition1963 := none
    instrumentCovariance := none
    terminalEpoch528 := none }

-- The matched C151#1 is IGRA Recife context, not a Caravelas measurement.
def caravelasComparisonContext : MatrixRef :=
  { snapshot := "a7978c3a75a153b16ab70118a92c434bba674cb7"
    label := 151, variant := 1 }

end Conde1963

-- ABELHA_CARAVELAS_VECTOR_CANDIDATE_BEGIN
/-! Three derived daily means from ONE archived NOAA station, not three
independent observations and not a measurement at Conde. The units
are signed millimetres per second (not uncertainties). -/
namespace Conde1963
structure ArchivedDailyWindVector where
  dateUTC : String
  stationHours : Nat
  calmHours : Nat
  uMillimetresPerSecond : Int
  vMillimetresPerSecond : Int
  scalarSpeedMillimetresPerSecond : Nat
  deriving Repr

def caravelasDailyVectors : List ArchivedDailyWindVector :=
[
  { dateUTC := "1963-11-07"
    stationHours := 24
    calmHours := 0
    uMillimetresPerSecond := -2709
    vMillimetresPerSecond := -1702
    scalarSpeedMillimetresPerSecond := 3367 },
  { dateUTC := "1963-11-08"
    stationHours := 24
    calmHours := 3
    uMillimetresPerSecond := -2334
    vMillimetresPerSecond := -2382
    scalarSpeedMillimetresPerSecond := 3367 },
  { dateUTC := "1963-11-09"
    stationHours := 24
    calmHours := 1
    uMillimetresPerSecond := -2372
    vMillimetresPerSecond := -2812
    scalarSpeedMillimetresPerSecond := 3775 }
]
end Conde1963
-- ABELHA_CARAVELAS_VECTOR_CANDIDATE_END
