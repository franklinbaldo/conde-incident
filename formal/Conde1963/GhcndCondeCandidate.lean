import Conde1963.Documentary

/-!
NOAA GHCN-Daily archival PRCP values on 7-9 Nov 1963. Typed documentary
inputs only. The historical gauge, observing-day clock, 1963 station
coordinates, measurement covariance and incident location are unverified.
A rainfall record cannot constrain a satellite trajectory without an
independent, calibrated transfer model.
-/

namespace Conde1963

structure ArchivedDailyPrecipitationCandidate where
  sourceId : String
  stationId : String
  wholeFileSha256 : String
  sourceFlag : String
  dayLabels : List String
  prcpTenthsMm : List Nat
  stationCoordsVerified1963 : Option String
  observingDayClock : Option String
  measurementCovariance : Option String
  incidentSiteRainfall : Option String
  orbitalTransfer : Option String
  latentParameter : String
  status : String
  deriving Repr

def ghcndCondeRain1963 : ArchivedDailyPrecipitationCandidate :=
  { sourceId := "MET-GHCND-CONDE-19631107-09-01"
    stationId := "BR048346820"
    wholeFileSha256 := "f99557d7cb4187ea412b85b205ad2b04bf7449c0b89d27d4f546f75cbc717d53"
    sourceFlag := "I"
    dayLabels := ["1963-11-07", "1963-11-08", "1963-11-09"]
    prcpTenthsMm := [0, 35, 0]
    stationCoordsVerified1963 := none
    observingDayClock := none
    measurementCovariance := none
    incidentSiteRainfall := none
    orbitalTransfer := none
    latentParameter := "precipitation_at_incident_site_and_epoch_unknown"
    status := "CONNECTED_PENDING_SPATIOTEMPORAL_CALIBRATION" }

def ghcndIndiarobaRain1963 : ArchivedDailyPrecipitationCandidate :=
  { ghcndCondeRain1963 with
    stationId := "BR048340980"
    wholeFileSha256 := "841a054af83f0b9c005744b96dfc4d0d66e8ceb55f836f9a1499bfbec0e4fa31"
    prcpTenthsMm := [0, 24, 0] }

end Conde1963
