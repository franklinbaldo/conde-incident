import Conde1963.Documentary

/-!
C241-L33, United Nations 1963 registration by the United States.
The status cutoffs are administrative. They are NOT instrument observation
UTCs, verified terminal event times, nor independent NASA/NORAD sensors.
Every physical dependency remains uncalibrated and inactive.
-/
namespace Conde1963

structure Un1963RegisteredElements where
  sourceOccurrence : String
  designator : String
  noradFromNasa1977 : Nat
  reportCutoffPrinted : String
  nodalPeriodMinPrinted : String
  inclinationDegPrinted : String
  apogeeKmPrinted : String
  perigeeKmPrinted : String
  instrumentEpochUtc : Option String
  covariance : Option String
  activeAsPhysics : Bool
  deriving Repr

def un1963RegistrationElements : List Un1963RegisteredElements :=
  [ { sourceOccurrence := "C241-L33:UN-INF30", designator := "1963-3-A",
      noradFromNasa1977 := 527, reportCutoffPrinted := "2400Z 31 JANUARY 1963",
      nodalPeriodMinPrinted := "94.7", inclinationDegPrinted := "81.97",
      apogeeKmPrinted := "518.6", perigeeKmPrinted := "479.5",
      instrumentEpochUtc := none, covariance := none, activeAsPhysics := false },
    { sourceOccurrence := "C241-L33:UN-INF30", designator := "1963-3-B",
      noradFromNasa1977 := 528, reportCutoffPrinted := "2400Z 31 JANUARY 1963",
      nodalPeriodMinPrinted := "94.5", inclinationDegPrinted := "81.97",
      apogeeKmPrinted := "505.5", perigeeKmPrinted := "476.4",
      instrumentEpochUtc := none, covariance := none, activeAsPhysics := false },
    { sourceOccurrence := "C241-L33:UN-INF30", designator := "1963-3-C",
      noradFromNasa1977 := 529, reportCutoffPrinted := "2400Z 31 JANUARY 1963",
      nodalPeriodMinPrinted := "94.7", inclinationDegPrinted := "81.97",
      apogeeKmPrinted := "525.5", perigeeKmPrinted := "476.4",
      instrumentEpochUtc := none, covariance := none, activeAsPhysics := false } ]

structure Un1963ReportedStatus where
  sourceOccurrence : String
  designator : String
  reportedNotOrbitByCutoff : String
  nasaReportedDecayDay : String
  terminalEpochUtc : Option String
  reportingErrorSeconds : Option Nat
  independentSensor : Bool
  activeAsPhysics : Bool
  deriving Repr

def un1963Reported528Status : Un1963ReportedStatus :=
  { sourceOccurrence := "C241-L33:UN-INF53", designator := "1963-3B",
    reportedNotOrbitByCutoff := "2400Z 15 NOVEMBER 1963",
    nasaReportedDecayDay := "1963-11-08", terminalEpochUtc := none,
    reportingErrorSeconds := none, independentSensor := false,
    activeAsPhysics := false }

end Conde1963
