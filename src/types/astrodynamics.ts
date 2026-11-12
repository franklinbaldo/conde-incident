export type EpistemicClassification =
  | 'DOCUMENTO_PRIMARIO_VERIFICADO'
  | 'FONTE_SECUNDARIA'
  | 'INFERENCIA_DINAMICA'
  | 'HIPOTESE';

export interface EpistemicItem {
  id: string;
  statement: string;
  classification: EpistemicClassification;
  source: string;
  notes: string;
}

export interface NoradObservationEvent {
  id: string;
  order: number;
  timestampMs: number;
  utcString: string;
  localTimeString: string; // Bahia / UTC-3
  titlePt: string;
  titleEn: string;
  authority: string;
  classification: EpistemicClassification;
  descriptionPt: string;
  descriptionEn: string;
  status528: string;
  status527: string;
  status529: string;
  focalObject: 527 | 528 | 529 | 'ALL';
}

export interface OrbitalElements {
  noradId: number;
  intlDesignator: string;
  name: string;
  epochStr: string;
  epochDate: Date;
  inclinationDeg: number;
  raanDeg: number;
  eccentricity: number;
  argPerigeeDeg: number;
  meanAnomalyDeg: number;
  meanMotionRevDay: number;
  bstar: number;
  semiMajorAxisKm: number;
  periodMin: number;
  meanAltitudeKm: number;
  line1: string;
  line2: string;
  decayDateCataloged: string;
  provenance: string;
  classification: EpistemicClassification;
}

export interface GeodeticCoordinate {
  latitude: number; // degrees (-90 to +90)
  longitude: number; // degrees (-180 to +180)
  altitudeKm: number;
}

export interface GroundTrackPoint extends GeodeticCoordinate {
  timestamp: number; // ms
  velocityKmS: number;
  inSunlight: boolean;
  distanceToCondeKm: number;
  elevationFromCondeDeg: number;
}

export interface UncertaintyEnvelope {
  center: GroundTrackPoint;
  leftLat: number;
  leftLon: number;
  rightLat: number;
  rightLon: number;
  crossTrackKm: number;
  alongTrackKm: number;
  sigmaKm: number;
  daysFromTleEpoch: number;
}

export interface CandidatePass {
  revolutionNumber: number;
  epochMs: number;
  utcString: string;
  localTimeString: string; // UTC-3
  closestApproachDistanceKm: number;
  subSatelliteLat: number;
  subSatelliteLon: number;
  altitudeKm: number;
  velocityKmS: number;
  elevationDeg: number;
  azimuthDeg: number;
  passType: 'ASCENDING' | 'DESCENDING';
  notes: string;
}

export interface TriangulationState {
  timestampMs: number;
  timeSinceLaunchDays: number;
  sat527: {
    altitudeKm: number;
    raanDeg: number;
    meanMotion: number;
  };
  sat528: {
    altitudeKm: number;
    raanDeg: number;
    meanMotion: number;
  };
  sat529: {
    altitudeKm: number;
    raanDeg: number;
    meanMotion: number;
  };
  deltaRaan528_527: number;
  deltaRaan528_529: number;
}

export interface MonteCarloRunResult {
  runId: number;
  decayTimestampMs: number;
  decayUtcString: string;
  reentryLat: number;
  reentryLon: number;
  ballisticCoeff: number;
  scaleHeightKm: number;
  solarFluxF107: number;
  distanceToCondeKm: number;
  isWithinConde100Km: boolean;
  isWithinConde500Km: boolean;
  latitudePassesCondeBand: boolean;
}

export interface SensitivityDataPoint {
  scaleHeightKm: number;
  simulatedDecayDate: string;
  simulatedDecayEpochMs: number;
  meanAltitudeAtCondePassKm: number;
  matchesCatalogNov8: boolean;
}

export interface TrackPassBenchmark {
  satelliteId: 527 | 529;
  satelliteName: string;
  passType: 'PAST' | 'FUTURE';
  time: Date;
  deltaMinutes: number; // e.g. -48 min or +45 min
  point: GroundTrackPoint;
  distanceKm: number;
  latitude: number;
  longitude: number;
  altitudeKm: number;
}

export interface InterTrackProximityData {
  referencePoint: {
    latitude: number;
    longitude: number;
    altitudeKm: number;
    timestampMs: number;
  };
  past527: TrackPassBenchmark;
  future527: TrackPassBenchmark;
  past529: TrackPassBenchmark;
  future529: TrackPassBenchmark;
  corridorWidth527Km: number; // Distance between 527 past track and 527 future track
  bracketingVerdict: string;
}
