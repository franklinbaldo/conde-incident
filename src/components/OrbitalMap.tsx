import React, { useState, useEffect, useRef, useMemo } from 'react';
import {
  Play,
  Pause,
  RotateCcw,
  FastForward,
  Compass,
  Globe2,
  Map as MapIcon,
  Eye,
  Crosshair,
  Clock,
  Layers,
  ChevronRight,
  ChevronLeft,
  Calendar,
  CheckCircle2,
  Info,
  Radio,
  X,
  ExternalLink,
  Satellite as SatelliteIcon,
  Maximize2,
  Anchor,
  ListFilter,
  MapPin,
  Sparkles,
  GitCommit,
} from 'lucide-react';
import {
  APIProvider,
  Map as GoogleMap,
  AdvancedMarker,
  Polyline as GooglePolyline,
  Circle as GoogleCircle,
  Pin,
  InfoWindow,
} from '@vis.gl/react-google-maps';
import {
  CONDE_COORDINATES,
  HISTORICAL_ORBITAL_DATA,
  NORAD_OBSERVATION_EVENTS,
  LAUNCH_MISSION,
} from '../lib/constants';
import { publicMilestones } from '../lib/publicMilestones';
import {
  propagateState,
  generateGroundTrack,
  computeGroundTrackWithUncertainty,
  getGreatCircleDistanceKm,
  computeInterTrackProximity,
  deg2rad,
  rad2deg,
} from '../lib/astrodynamics';
import {
  GroundTrackPoint,
  NoradObservationEvent,
  UncertaintyEnvelope,
  InterTrackProximityData,
} from '../types/astrodynamics';

interface OrbitalMapProps {
  lang: 'pt' | 'en';
  selectedTimeMs?: number;
  onTimeChange?: (timeMs: number) => void;
}

// World coastline polygon approximation for crisp canvas fallback / rendering
const WORLD_LANDMASS_OUTLINES = [
  // North America
  [[-168,65],[-140,70],[-120,72],[-80,72],[-60,50],[-70,42],[-80,25],[-95,20],[-105,22],[-120,34],[-125,48],[-140,58],[-165,65]],
  // South America
  [[-80,10],[-60,8],[-50,0],[-35,-5],[-37,-12],[-40,-22],[-50,-30],[-60,-40],[-68,-55],[-75,-48],[-72,-30],[-80,-5],[-80,10]],
  // Eurasia
  [[-10,36],[0,44],[10,55],[25,70],[60,70],[100,75],[140,70],[170,65],[140,40],[120,30],[105,10],[80,10],[60,25],[45,40],[30,30],[10,36],[-10,36]],
  // Africa
  [[-15,35],[10,37],[32,30],[42,12],[50,10],[40,-10],[30,-34],[18,-34],[10,-5],[-15,10],[-17,25],[-15,35]],
  // Australia
  [[115,-20],[130,-12],[145,-15],[150,-24],[152,-38],[138,-35],[115,-35],[115,-20]],
  // Antarctica
  [[-180,-70],[180,-70],[180,-85],[-180,-85]],
];

const LAUNCH_MS = new Date('1963-01-16T21:59:00Z').getTime();
const END_OF_1963_MS = new Date('1963-12-31T23:59:59Z').getTime();
// Day-only catalogue entries and a claimed Conde encounter are not measured fixes.
const displayedMilestones = publicMilestones(NORAD_OBSERVATION_EVENTS);

export const OrbitalMap: React.FC<OrbitalMapProps> = ({
  lang,
  selectedTimeMs: externalTimeMs,
  onTimeChange,
}) => {
  const isPt = lang === 'pt';
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  // Simulation time state: defaults to launch epoch or external
  const [simTimeMs, setSimTimeMs] = useState<number>(
    externalTimeMs || LAUNCH_MS
  );
  const [isPlaying, setIsPlaying] = useState<boolean>(false);
  const [playbackSpeed, setPlaybackSpeed] = useState<number>(3600); // default: 1 hour/sec

  // Map view modes: 'google-earth' (Google Maps Satellite), '2D' (Canvas Equirectangular), '3D' (Canvas Globe)
  const [mapMode, setMapMode] = useState<'google-earth' | '2D' | '3D'>('google-earth');
  const [showSisterSatellites, setShowSisterSatellites] = useState<boolean>(true);
  const [showHorizonMasks, setShowHorizonMasks] = useState<boolean>(true);
  const [showUncertaintyBuffer, setShowUncertaintyBuffer] = useState<boolean>(false);
  const [showObservationMarkers, setShowObservationMarkers] = useState<boolean>(false);
  const [showInterTrackVectors, setShowInterTrackVectors] = useState<boolean>(true);

  // Google Maps specific camera control
  const [gmapZoom, setGmapZoom] = useState<number>(3);
  const [gmapCenter, setGmapCenter] = useState<{ lat: number; lng: number }>({
    lat: CONDE_COORDINATES.latitude,
    lng: CONDE_COORDINATES.longitude,
  });
  const [followSatellite, setFollowSatellite] = useState<boolean>(false);
  const [selectedPinSatellite, setSelectedPinSatellite] = useState<'528' | '527' | '529' | 'conde' | null>(null);
  const [hoveredObsEvent, setHoveredObsEvent] = useState<NoradObservationEvent | null>(null);

  // Auto-pause on NORAD observations feature
  const [pauseOnObservations, setPauseOnObservations] = useState<boolean>(false);
  const [activeObservationModal, setActiveObservationModal] = useState<NoradObservationEvent | null>(null);
  const [showAnchorsListDrawer, setShowAnchorsListDrawer] = useState<boolean>(false);
  const [selectedObsMarker, setSelectedObsMarker] = useState<any | null>(null);
  const lastTriggeredObsIdRef = useRef<string | null>(null);

  // 3D globe rotation angles (canvas 3D mode)
  const [globeRotY, setGlobeRotY] = useState<number>(40);
  const [globeRotX, setGlobeRotX] = useState<number>(-15);
  const isDraggingRef = useRef<boolean>(false);
  const lastMousePosRef = useRef<{ x: number; y: number }>({ x: 0, y: 0 });

  // API Key for Google Maps Platform
  const mapsApiKey = (import.meta.env.VITE_GOOGLE_MAPS_API_KEY as string) || '';

  // Sync external time changes
  useEffect(() => {
    if (externalTimeMs && externalTimeMs !== simTimeMs) {
      setSimTimeMs(externalTimeMs);
    }
  }, [externalTimeMs]);

  // Jump to specific timestamp
  const jumpToTime = (timeMs: number, obsEvent?: NoradObservationEvent) => {
    setSimTimeMs(timeMs);
    if (onTimeChange) onTimeChange(timeMs);
    if (obsEvent) {
      setActiveObservationModal(obsEvent);
      lastTriggeredObsIdRef.current = obsEvent.id;
    }
  };

  // Find current nearest or active observation milestone
  const currentObsIndex = useMemo(() => {
    let idx = 0;
    for (let i = 0; i < displayedMilestones.length; i++) {
      if (simTimeMs >= displayedMilestones[i].timestampMs) {
        idx = i;
      }
    }
    return idx;
  }, [simTimeMs]);

  // Step to Next / Previous observation
  const stepObservation = (direction: 'next' | 'prev') => {
    let targetIdx = direction === 'next' ? currentObsIndex + 1 : currentObsIndex - 1;
    if (targetIdx < 0) targetIdx = 0;
    if (targetIdx >= displayedMilestones.length) targetIdx = displayedMilestones.length - 1;
    const ev = displayedMilestones[targetIdx];
    setIsPlaying(false);
    jumpToTime(ev.timestampMs, ev);
  };

  // Explore epochs without treating a day-only decay as an observed terminal instant
  useEffect(() => {
    if (!isPlaying) return;

    const interval = setInterval(() => {
      setSimTimeMs((prev) => {
        const stepMs = (playbackSpeed * 1000) / 10;
        const next = prev + stepMs;

        // Auto-pause on exploratory timeline marks, never on a claimed impact.
        if (pauseOnObservations) {
          for (const ev of displayedMilestones) {
            if (
              prev < ev.timestampMs &&
              next >= ev.timestampMs &&
              lastTriggeredObsIdRef.current !== ev.id
            ) {
              lastTriggeredObsIdRef.current = ev.id;
              setIsPlaying(false);
              setActiveObservationModal(ev);
              return ev.timestampMs; // Snap exactly to observation second
            }
          }
        }

        if (next > END_OF_1963_MS) {
          setIsPlaying(false);
          return END_OF_1963_MS;
        }
        return next;
      });
    }, 100);

    return () => clearInterval(interval);
  }, [isPlaying, playbackSpeed, pauseOnObservations]);

  // Current Satellites Telemetry
  const curDate = useMemo(() => new Date(simTimeMs), [simTimeMs]);
  const sat528Point = useMemo(() => propagateState(528, curDate), [simTimeMs]);
  const sat527Point = useMemo(() => propagateState(527, curDate), [simTimeMs]);
  const sat529Point = useMemo(() => propagateState(529, curDate), [simTimeMs]);

  // Auto-center Google Earth camera on target satellite if "follow" enabled
  useEffect(() => {
    if (followSatellite && sat528Point && mapMode === 'google-earth') {
      setGmapCenter({
        lat: sat528Point.latitude,
        lng: sat528Point.longitude,
      });
    }
  }, [followSatellite, sat528Point, mapMode]);

  // Check decay statuses
  const is528Decayed = simTimeMs > new Date('1963-11-08T23:59:59Z').getTime();
  const is529Decayed = simTimeMs > new Date('1963-12-31T23:59:59Z').getTime();
  const isBeforeLaunch = simTimeMs < LAUNCH_MS;

  // Ground tracks and Epistemic Uncertainty Buffer for NORAD 528 (-45 min to +45 min)
  const track528Data = useMemo(() => {
    if (isBeforeLaunch || is528Decayed) return { points: [], envelopes: [] };
    const trackStart = new Date(simTimeMs - 45 * 60 * 1000);
    return computeGroundTrackWithUncertainty(528, trackStart, 90, 60);
  }, [simTimeMs, isBeforeLaunch, is528Decayed]);

  const track528 = track528Data.points;
  const envelopes528 = track528Data.envelopes;

  const track527 = useMemo(() => {
    if (isBeforeLaunch || !showSisterSatellites) return [];
    const trackStart = new Date(simTimeMs - 45 * 60 * 1000);
    return generateGroundTrack(527, trackStart, 90, 60);
  }, [simTimeMs, isBeforeLaunch, showSisterSatellites]);

  const track529 = useMemo(() => {
    if (isBeforeLaunch || is529Decayed || !showSisterSatellites) return [];
    const trackStart = new Date(simTimeMs - 45 * 60 * 1000);
    return generateGroundTrack(529, trackStart, 90, 60);
  }, [simTimeMs, isBeforeLaunch, is529Decayed, showSisterSatellites]);

  // Dynamic Inter-Track Proximity (528 relative to 527 and 529 past/future passes)
  const interTrackData = useMemo(() => {
    if (!sat528Point || isBeforeLaunch || is528Decayed) return null;
    return computeInterTrackProximity(
      sat528Point.latitude,
      sat528Point.longitude,
      sat528Point.altitudeKm,
      new Date(simTimeMs)
    );
  }, [sat528Point, isBeforeLaunch, is528Decayed, simTimeMs]);

  // Convert track to Google Maps LatLngLiteral chunks (split across antimeridian to prevent wrap lines)
  const splitTrackByAntimeridian = (track: GroundTrackPoint[]): Array<Array<{ lat: number; lng: number }>> => {
    if (track.length === 0) return [];
    const segments: Array<Array<{ lat: number; lng: number }>> = [];
    let currentSeg: Array<{ lat: number; lng: number }> = [];

    for (let i = 0; i < track.length; i++) {
      const pt = track[i];
      if (currentSeg.length > 0) {
        const prev = currentSeg[currentSeg.length - 1];
        if (Math.abs(pt.longitude - prev.lng) > 180) {
          segments.push(currentSeg);
          currentSeg = [];
        }
      }
      currentSeg.push({ lat: pt.latitude, lng: pt.longitude });
    }
    if (currentSeg.length > 0) segments.push(currentSeg);
    return segments;
  };

  // Convert uncertainty envelopes into Google Maps Polyline boundaries (left/right corridor rails)
  const splitUncertaintyRails = (envelopes: UncertaintyEnvelope[]) => {
    if (envelopes.length === 0) return { leftSegments: [], rightSegments: [] };
    const leftRails: Array<Array<{ lat: number; lng: number }>> = [];
    const rightRails: Array<Array<{ lat: number; lng: number }>> = [];
    let curLeft: Array<{ lat: number; lng: number }> = [];
    let curRight: Array<{ lat: number; lng: number }> = [];

    for (let i = 0; i < envelopes.length; i++) {
      const env = envelopes[i];
      if (curLeft.length > 0) {
        const prevL = curLeft[curLeft.length - 1];
        const prevR = curRight[curRight.length - 1];
        if (Math.abs(env.leftLon - prevL.lng) > 180 || Math.abs(env.rightLon - prevR.lng) > 180) {
          leftRails.push(curLeft);
          rightRails.push(curRight);
          curLeft = [];
          curRight = [];
        }
      }
      curLeft.push({ lat: env.leftLat, lng: env.leftLon });
      curRight.push({ lat: env.rightLat, lng: env.rightLon });
    }
    if (curLeft.length > 0) {
      leftRails.push(curLeft);
      rightRails.push(curRight);
    }
    return { leftSegments: leftRails, rightSegments: rightRails };
  };

  const googleTrack528Segments = useMemo(() => splitTrackByAntimeridian(track528), [track528]);
  const googleTrack527Segments = useMemo(() => splitTrackByAntimeridian(track527), [track527]);
  const googleTrack529Segments = useMemo(() => splitTrackByAntimeridian(track529), [track529]);
  const googleUncertaintyRails = useMemo(() => splitUncertaintyRails(envelopes528), [envelopes528]);

  // Pre-calculate positions and anchoring benchmarks for each historical NORAD observation epoch
  const noradObservationMarkers = useMemo(() => {
    return displayedMilestones.map((ev) => {
      const d = new Date(ev.timestampMs);
      const p528 = propagateState(528, d);
      const p527 = propagateState(527, d);
      const p529 = propagateState(529, d);

      // Determine focal anchor coordinate
      let lat = 0;
      let lng = 0;
      let altKm = 0;
      let shortLabel = ev.titlePt;
      let trackingStation = ev.authority;

      switch (ev.id) {
        case 'OBS-01':
          // Vandenberg AFB SLC-2W launch pad & polar injection
          lat = 34.748;
          lng = -120.618;
          altKm = 185;
          shortLabel = 'Injeção Orbital Vandenberg';
          trackingStation = 'SLC-2W, Vandenberg AFB (Califórnia)';
          break;
        case 'OBS-02':
          // Eglin AFB SPADATS radar acquisition
          lat = p528 ? p528.latitude : 28.52;
          lng = p528 ? p528.longitude : -85.18;
          altKm = p528 ? p528.altitudeKm : 362;
          shortLabel = '1ª Aquisição Radar SPADATS';
          trackingStation = 'Radar SPADATS / Eglin AFB (Flórida)';
          break;
        case 'OBS-03':
          lat = p528 ? p528.latitude : 38.99;
          lng = p528 ? p528.longitude : -76.85;
          altKm = p528 ? p528.altitudeKm : 358;
          shortLabel = 'Boletim NASA SSR Vol 3 Nº 2';
          trackingStation = 'NASA Goddard Space Flight Center';
          break;
        case 'OBS-04':
          lat = p528 ? p528.latitude : 45.2;
          lng = p528 ? p528.longitude : -110.5;
          altKm = p528 ? p528.altitudeKm : 351;
          shortLabel = 'Auditoria Nodal SPADATS';
          trackingStation = '1st Aerospace Surveillance Wing (NORAD)';
          break;
        case 'OBS-05':
          // NORAD 527 TLE Epoch
          lat = p527 ? p527.latitude : 25.1;
          lng = p527 ? p527.longitude : -45.3;
          altKm = p527 ? p527.altitudeKm : 485;
          shortLabel = 'Época TLE NORAD 527 (OPS 0180)';
          trackingStation = 'Space-Track / USAF SPADATS 63300.5';
          break;
        case 'OBS-06':
          // NORAD 528 TLE Epoch
          lat = p528 ? p528.latitude : 15.3;
          lng = p528 ? p528.longitude : -35.2;
          altKm = p528 ? p528.altitudeKm : 345;
          shortLabel = 'Última Efeméride NORAD 528';
          trackingStation = 'Space-Track / USAF SPADATS 63300.61';
          break;
        case 'OBS-09':
          // NASA SSR Vol 3 #22
          lat = p527 ? p527.latitude : -18.2;
          lng = p527 ? p527.longitude : -25.4;
          altKm = p527 ? p527.altitudeKm : 485;
          shortLabel = 'NASA SSR (528 Ausente do Catálogo)';
          trackingStation = 'NASA GSFC Situation Report';
          break;
        case 'OBS-10':
          // NORAD 529 TLE Epoch
          lat = p529 ? p529.latitude : 42.1;
          lng = p529 ? p529.longitude : -60.2;
          altKm = p529 ? p529.altitudeKm : 247;
          shortLabel = 'Último TLE NORAD 529';
          trackingStation = 'Space-Track / SPADATS 63364.47';
          break;
        default:
          lat = p528 ? p528.latitude : 0;
          lng = p528 ? p528.longitude : 0;
          altKm = p528 ? p528.altitudeKm : 300;
          shortLabel = ev.titlePt;
          trackingStation = ev.authority;
      }

      const distanceToCondeKm = Math.round(
        getGreatCircleDistanceKm(
          lat,
          lng,
          CONDE_COORDINATES.latitude,
          CONDE_COORDINATES.longitude
        )
      );

      const latCard = lat >= 0 ? `${lat.toFixed(2)}°N` : `${Math.abs(lat).toFixed(2)}°S`;
      const lngCard = lng >= 0 ? `${lng.toFixed(2)}°L` : `${Math.abs(lng).toFixed(2)}°O`;
      const formattedCoord = `${latCard}, ${lngCard}`;

      return {
        event: ev,
        position: { lat, lng },
        altitudeKm: altKm,
        formattedCoord,
        distanceToCondeKm,
        shortLabel,
        trackingStation,
        p528,
        p527,
        p529,
        isPast: simTimeMs >= ev.timestampMs,
        isCurrent: displayedMilestones[currentObsIndex]?.id === ev.id,
      };
    });
  }, [simTimeMs, currentObsIndex]);

  // Canvas Rendering (2D & 3D)
  useEffect(() => {
    if (mapMode === 'google-earth') return;
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const width = canvas.width;
    const height = canvas.height;

    ctx.clearRect(0, 0, width, height);

    if (mapMode === '2D') {
      render2DMap(ctx, width, height);
    } else {
      render3DGlobe(ctx, width, height);
    }
  }, [
    mapMode,
    simTimeMs,
    sat528Point,
    sat527Point,
    sat529Point,
    track528,
    track527,
    track529,
    globeRotX,
    globeRotY,
    showHorizonMasks,
    showSisterSatellites,
    isBeforeLaunch,
    is528Decayed,
  ]);

  // Render 2D Equirectangular Map
  const render2DMap = (ctx: CanvasRenderingContext2D, width: number, height: number) => {
    ctx.fillStyle = '#090d16';
    ctx.fillRect(0, 0, width, height);

    const toScreen = (lon: number, lat: number) => {
      const x = ((lon + 180) / 360) * width;
      const y = ((90 - lat) / 180) * height;
      return { x, y };
    };

    // Draw Grid Lines (Meridians & Parallels)
    ctx.strokeStyle = '#182234';
    ctx.lineWidth = 1;
    ctx.setLineDash([2, 4]);

    for (let lat = -80; lat <= 80; lat += 20) {
      ctx.beginPath();
      ctx.moveTo(0, ((90 - lat) / 180) * height);
      ctx.lineTo(width, ((90 - lat) / 180) * height);
      ctx.stroke();
    }
    for (let lon = -180; lon <= 180; lon += 30) {
      ctx.beginPath();
      ctx.moveTo(((lon + 180) / 360) * width, 0);
      ctx.lineTo(((lon + 180) / 360) * width, height);
      ctx.stroke();
    }
    ctx.setLineDash([]);

    // Highlight Equator
    ctx.strokeStyle = '#25354e';
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.moveTo(0, height / 2);
    ctx.lineTo(width, height / 2);
    ctx.stroke();

    // Highlight Conde Parallel (-11.8139°)
    const condeY = ((90 - CONDE_COORDINATES.latitude) / 180) * height;
    ctx.strokeStyle = '#f43f5e55';
    ctx.setLineDash([4, 4]);
    ctx.beginPath();
    ctx.moveTo(0, condeY);
    ctx.lineTo(width, condeY);
    ctx.stroke();
    ctx.setLineDash([]);

    ctx.fillStyle = '#f43f5e';
    ctx.font = '10px monospace';
    ctx.fillText('Paralelo de Conde (-11,81°)', 10, condeY - 4);

    // Draw Continents
    ctx.fillStyle = '#162235';
    ctx.strokeStyle = '#273b5b';
    ctx.lineWidth = 1;

    WORLD_LANDMASS_OUTLINES.forEach((poly) => {
      ctx.beginPath();
      poly.forEach(([lon, lat], idx) => {
        const { x, y } = toScreen(lon, lat);
        if (idx === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      });
      ctx.closePath();
      ctx.fill();
      ctx.stroke();
    });

    // Draw Conde Target & Horizons
    const condePos = toScreen(CONDE_COORDINATES.longitude, CONDE_COORDINATES.latitude);

    if (showHorizonMasks) {
      const r500 = (500 / 40075) * width;
      ctx.fillStyle = '#f43f5e0a';
      ctx.strokeStyle = '#f43f5e33';
      ctx.beginPath();
      ctx.arc(condePos.x, condePos.y, r500, 0, Math.PI * 2);
      ctx.fill();
      ctx.stroke();

      const r250 = (250 / 40075) * width;
      ctx.fillStyle = '#f43f5e15';
      ctx.strokeStyle = '#f43f5e66';
      ctx.beginPath();
      ctx.arc(condePos.x, condePos.y, r250, 0, Math.PI * 2);
      ctx.fill();
      ctx.stroke();

      const r100 = (100 / 40075) * width;
      ctx.fillStyle = '#f43f5e30';
      ctx.strokeStyle = '#f43f5e';
      ctx.beginPath();
      ctx.arc(condePos.x, condePos.y, r100, 0, Math.PI * 2);
      ctx.fill();
      ctx.stroke();
    }

    // Target Pin Conde
    ctx.fillStyle = '#fb7185';
    ctx.beginPath();
    ctx.arc(condePos.x, condePos.y, 4, 0, Math.PI * 2);
    ctx.fill();
    ctx.strokeStyle = '#ffffff';
    ctx.lineWidth = 1.5;
    ctx.stroke();
    ctx.fillStyle = '#ffffff';
    ctx.font = 'bold 11px sans-serif';
    ctx.fillText('CONDE, BA', condePos.x + 8, condePos.y + 3);

    // Draw Ground Tracks for 527 (OPS 0180) in Emerald
    if (showSisterSatellites && track527.length > 1) {
      ctx.lineWidth = 1.5;
      ctx.strokeStyle = '#10b98188';
      for (let i = 0; i < track527.length - 1; i++) {
        const p1 = track527[i];
        const p2 = track527[i + 1];
        if (Math.abs(p1.longitude - p2.longitude) > 180) continue;
        const s1 = toScreen(p1.longitude, p1.latitude);
        const s2 = toScreen(p2.longitude, p2.latitude);
        ctx.beginPath();
        ctx.moveTo(s1.x, s1.y);
        ctx.lineTo(s2.x, s2.y);
        ctx.stroke();
      }
    }

    // Draw Ground Tracks for 529 in Purple
    if (showSisterSatellites && track529.length > 1) {
      ctx.lineWidth = 1.5;
      ctx.strokeStyle = '#c084fc88';
      for (let i = 0; i < track529.length - 1; i++) {
        const p1 = track529[i];
        const p2 = track529[i + 1];
        if (Math.abs(p1.longitude - p2.longitude) > 180) continue;
        const s1 = toScreen(p1.longitude, p1.latitude);
        const s2 = toScreen(p2.longitude, p2.latitude);
        ctx.beginPath();
        ctx.moveTo(s1.x, s1.y);
        ctx.lineTo(s2.x, s2.y);
        ctx.stroke();
      }
    }

    // Draw exploratory spread only: not a probability or calibrated interval
    if (showUncertaintyBuffer && envelopes528.length > 1) {
      for (let i = 0; i < envelopes528.length - 1; i++) {
        const e1 = envelopes528[i];
        const e2 = envelopes528[i + 1];
        if (
          Math.abs(e1.center.longitude - e2.center.longitude) > 180 ||
          Math.abs(e1.leftLon - e2.leftLon) > 180 ||
          Math.abs(e1.rightLon - e2.rightLon) > 180
        ) {
          continue;
        }

        const l1 = toScreen(e1.leftLon, e1.leftLat);
        const l2 = toScreen(e2.leftLon, e2.leftLat);
        const r2 = toScreen(e2.rightLon, e2.rightLat);
        const r1 = toScreen(e1.rightLon, e1.rightLat);

        // Fill semi-transparent uncertainty corridor
        ctx.fillStyle = 'rgba(6, 182, 212, 0.12)';
        ctx.beginPath();
        ctx.moveTo(l1.x, l1.y);
        ctx.lineTo(l2.x, l2.y);
        ctx.lineTo(r2.x, r2.y);
        ctx.lineTo(r1.x, r1.y);
        ctx.closePath();
        ctx.fill();

        // Draw boundary dashed rails
        ctx.strokeStyle = 'rgba(34, 211, 238, 0.35)';
        ctx.lineWidth = 1;
        ctx.setLineDash([3, 3]);
        ctx.beginPath();
        ctx.moveTo(l1.x, l1.y);
        ctx.lineTo(l2.x, l2.y);
        ctx.stroke();

        ctx.beginPath();
        ctx.moveTo(r1.x, r1.y);
        ctx.lineTo(r2.x, r2.y);
        ctx.stroke();
        ctx.setLineDash([]);
      }
    }

    // Draw Ground Track for 528 (Target) in Cyan/Amber/Red
    if (track528.length > 1) {
      ctx.lineWidth = 2.5;
      for (let i = 0; i < track528.length - 1; i++) {
        const p1 = track528[i];
        const p2 = track528[i + 1];
        if (Math.abs(p1.longitude - p2.longitude) > 180) continue;
        const s1 = toScreen(p1.longitude, p1.latitude);
        const s2 = toScreen(p2.longitude, p2.latitude);

        if (p1.altitudeKm > 180) {
          ctx.strokeStyle = '#22d3ee';
        } else if (p1.altitudeKm >= 80) {
          ctx.strokeStyle = '#fbbf24';
        } else {
          ctx.strokeStyle = '#ef4444';
        }

        ctx.beginPath();
        ctx.moveTo(s1.x, s1.y);
        ctx.lineTo(s2.x, s2.y);
        ctx.stroke();
      }
    }

    // Draw Sub-Satellite Points
    if (sat527Point && showSisterSatellites) {
      const p527 = toScreen(sat527Point.longitude, sat527Point.latitude);
      ctx.fillStyle = '#10b981';
      ctx.beginPath();
      ctx.arc(p527.x, p527.y, 4, 0, Math.PI * 2);
      ctx.fill();
      ctx.strokeStyle = '#ffffff';
      ctx.lineWidth = 1;
      ctx.stroke();
      ctx.fillStyle = '#10b981';
      ctx.font = '10px monospace';
      ctx.fillText(`527 [${sat527Point.altitudeKm.toFixed(0)} km]`, p527.x + 8, p527.y - 3);
    }

    if (sat529Point && showSisterSatellites) {
      const p529 = toScreen(sat529Point.longitude, sat529Point.latitude);
      ctx.fillStyle = '#c084fc';
      ctx.beginPath();
      ctx.arc(p529.x, p529.y, 4, 0, Math.PI * 2);
      ctx.fill();
      ctx.strokeStyle = '#ffffff';
      ctx.lineWidth = 1;
      ctx.stroke();
      ctx.fillStyle = '#c084fc';
      ctx.font = '10px monospace';
      ctx.fillText(`529 [${sat529Point.altitudeKm.toFixed(0)} km]`, p529.x + 8, p529.y - 3);
    }

    // Draw Historical NORAD Observation Anchor Markers on 2D Map
    if (showObservationMarkers) {
      noradObservationMarkers.forEach((marker) => {
        const pos = toScreen(marker.position.lng, marker.position.lat);
        const isCurrent = marker.isCurrent;

        // Outer milestone diamond
        ctx.save();
        ctx.translate(pos.x, pos.y);
        ctx.rotate(Math.PI / 4);

        if (isCurrent) {
          ctx.fillStyle = '#f59e0b';
          ctx.strokeStyle = '#ffffff';
          ctx.lineWidth = 2;
          ctx.fillRect(-6, -6, 12, 12);
          ctx.strokeRect(-6, -6, 12, 12);
        } else {
          ctx.fillStyle = marker.isPast ? 'rgba(6, 182, 212, 0.7)' : 'rgba(113, 113, 122, 0.5)';
          ctx.strokeStyle = marker.isPast ? '#22d3ee' : '#71717a';
          ctx.lineWidth = 1;
          ctx.fillRect(-4, -4, 8, 8);
          ctx.strokeRect(-4, -4, 8, 8);
        }
        ctx.restore();

        // Milestone number badge and date
        ctx.fillStyle = isCurrent ? '#fbbf24' : marker.isPast ? '#67e8f9' : '#a1a1aa';
        ctx.font = 'bold 9px monospace';
        ctx.fillText(`#${marker.event.order} (${marker.event.utcString.substring(5, 10)})`, pos.x + 8, pos.y + 3);
      });
    }

    if (sat528Point) {
      const satPos = toScreen(sat528Point.longitude, sat528Point.latitude);
      ctx.strokeStyle = sat528Point.altitudeKm < 120 ? '#ef4444' : '#22d3ee';
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.arc(satPos.x, satPos.y, 11, 0, Math.PI * 2);
      ctx.stroke();

      ctx.fillStyle = sat528Point.altitudeKm < 120 ? '#ef4444' : '#06b6d4';
      ctx.beginPath();
      ctx.arc(satPos.x, satPos.y, 5, 0, Math.PI * 2);
      ctx.fill();

      ctx.fillStyle = '#22d3ee';
      ctx.font = 'bold 11px monospace';
      ctx.fillText(`NORAD 528 [${sat528Point.altitudeKm.toFixed(0)} km]`, satPos.x + 14, satPos.y - 4);

      if (sat528Point.distanceToCondeKm <= 2500) {
        ctx.strokeStyle = '#f43f5e99';
        ctx.setLineDash([3, 3]);
        ctx.lineWidth = 1.5;
        ctx.beginPath();
        ctx.moveTo(satPos.x, satPos.y);
        ctx.lineTo(condePos.x, condePos.y);
        ctx.stroke();
        ctx.setLineDash([]);
      }
    } else if (is528Decayed) {
      ctx.fillStyle = '#ef4444cc';
      ctx.font = 'bold 12px monospace';
      ctx.fillText('NORAD 528: DECAÍDO / REENTROU (08/11/1963)', 20, height - 20);
    }
  };

  // Render 3D Orthographic Globe
  const render3DGlobe = (ctx: CanvasRenderingContext2D, width: number, height: number) => {
    ctx.fillStyle = '#05070d';
    ctx.fillRect(0, 0, width, height);

    const cx = width / 2;
    const cy = height / 2;
    const radius = Math.min(width, height) * 0.42;

    const glow = ctx.createRadialGradient(cx, cy, radius * 0.95, cx, cy, radius * 1.12);
    glow.addColorStop(0, 'rgba(6, 182, 212, 0.35)');
    glow.addColorStop(1, 'rgba(6, 182, 212, 0)');
    ctx.fillStyle = glow;
    ctx.beginPath();
    ctx.arc(cx, cy, radius * 1.12, 0, Math.PI * 2);
    ctx.fill();

    ctx.fillStyle = '#0d1527';
    ctx.beginPath();
    ctx.arc(cx, cy, radius, 0, Math.PI * 2);
    ctx.fill();
    ctx.strokeStyle = '#1e293b';
    ctx.lineWidth = 2;
    ctx.stroke();

    const project3D = (lonDeg: number, latDeg: number) => {
      let lon = deg2rad(lonDeg + globeRotY);
      let lat = deg2rad(latDeg);
      const rotX = deg2rad(globeRotX);

      let x = Math.cos(lat) * Math.sin(lon);
      let y = Math.sin(lat);
      let z = Math.cos(lat) * Math.cos(lon);

      const yNew = y * Math.cos(rotX) - z * Math.sin(rotX);
      const zNew = y * Math.sin(rotX) + z * Math.cos(rotX);

      return {
        screenX: cx + x * radius,
        screenY: cy - yNew * radius,
        visible: zNew > 0,
      };
    };

    ctx.fillStyle = '#1a273e';
    ctx.strokeStyle = '#2e4368';
    ctx.lineWidth = 1;

    WORLD_LANDMASS_OUTLINES.forEach((poly) => {
      ctx.beginPath();
      let first = true;
      poly.forEach(([lon, lat]) => {
        const pt = project3D(lon, lat);
        if (pt.visible) {
          if (first) {
            ctx.moveTo(pt.screenX, pt.screenY);
            first = false;
          } else {
            ctx.lineTo(pt.screenX, pt.screenY);
          }
        }
      });
      ctx.stroke();
    });

    const conde3D = project3D(CONDE_COORDINATES.longitude, CONDE_COORDINATES.latitude);
    if (conde3D.visible) {
      ctx.fillStyle = '#f43f5e';
      ctx.beginPath();
      ctx.arc(conde3D.screenX, conde3D.screenY, 5, 0, Math.PI * 2);
      ctx.fill();
      ctx.fillStyle = '#ffffff';
      ctx.font = 'bold 10px sans-serif';
      ctx.fillText('Conde, BA', conde3D.screenX + 8, conde3D.screenY + 3);
    }

    if (sat527Point && showSisterSatellites) {
      const p = project3D(sat527Point.longitude, sat527Point.latitude);
      if (p.visible) {
        ctx.fillStyle = '#10b981';
        ctx.beginPath();
        ctx.arc(p.screenX, p.screenY, 4, 0, Math.PI * 2);
        ctx.fill();
        ctx.fillText('527', p.screenX + 6, p.screenY - 2);
      }
    }

    if (sat529Point && showSisterSatellites) {
      const p = project3D(sat529Point.longitude, sat529Point.latitude);
      if (p.visible) {
        ctx.fillStyle = '#c084fc';
        ctx.beginPath();
        ctx.arc(p.screenX, p.screenY, 4, 0, Math.PI * 2);
        ctx.fill();
        ctx.fillText('529', p.screenX + 6, p.screenY - 2);
      }
    }

    if (sat528Point) {
      const sat3D = project3D(sat528Point.longitude, sat528Point.latitude);
      if (sat3D.visible) {
        ctx.fillStyle = '#06b6d4';
        ctx.beginPath();
        ctx.arc(sat3D.screenX, sat3D.screenY, 6, 0, Math.PI * 2);
        ctx.fill();
        ctx.strokeStyle = '#ffffff';
        ctx.lineWidth = 2;
        ctx.stroke();

        ctx.fillStyle = '#22d3ee';
        ctx.font = 'bold 11px monospace';
        ctx.fillText(`528 (${sat528Point.altitudeKm.toFixed(0)} km)`, sat3D.screenX + 10, sat3D.screenY - 4);
      }
    }

    // Draw NORAD Observation Anchor Markers on 3D Globe
    if (showObservationMarkers) {
      noradObservationMarkers.forEach((marker) => {
        const p3d = project3D(marker.position.lng, marker.position.lat);
        if (!p3d.visible) return;
        ctx.save();
        ctx.translate(p3d.screenX, p3d.screenY);
        ctx.rotate(Math.PI / 4);
        if (marker.isCurrent) {
          ctx.fillStyle = '#f59e0b';
          ctx.fillRect(-5, -5, 10, 10);
        } else {
          ctx.fillStyle = marker.isPast ? '#06b6d4' : '#71717a';
          ctx.fillRect(-3, -3, 6, 6);
        }
        ctx.restore();
        ctx.fillStyle = marker.isCurrent ? '#fbbf24' : '#a1a1aa';
        ctx.font = '9px monospace';
        ctx.fillText(`#${marker.event.order}`, p3d.screenX + 6, p3d.screenY + 2);
      });
    }
  };

  const handleMouseDown = (e: React.MouseEvent<HTMLCanvasElement>) => {
    if (mapMode !== '3D') return;
    isDraggingRef.current = true;
    lastMousePosRef.current = { x: e.clientX, y: e.clientY };
  };

  const handleMouseMove = (e: React.MouseEvent<HTMLCanvasElement>) => {
    if (!isDraggingRef.current || mapMode !== '3D') return;
    const dx = e.clientX - lastMousePosRef.current.x;
    const dy = e.clientY - lastMousePosRef.current.y;
    setGlobeRotY((prev) => prev + dx * 0.5);
    setGlobeRotX((prev) => Math.max(-85, Math.min(85, prev - dy * 0.5)));
    lastMousePosRef.current = { x: e.clientX, y: e.clientY };
  };

  const handleMouseUp = () => {
    isDraggingRef.current = false;
  };

  // Focus view directly on Conde
  const centerOnConde = () => {
    setFollowSatellite(false);
    setGmapCenter({
      lat: CONDE_COORDINATES.latitude,
      lng: CONDE_COORDINATES.longitude,
    });
    setGmapZoom(7);
  };

  // Focus view directly on 528
  const centerOn528 = () => {
    if (sat528Point) {
      setFollowSatellite(true);
      setGmapCenter({
        lat: sat528Point.latitude,
        lng: sat528Point.longitude,
      });
      setGmapZoom(5);
    }
  };

  return (
    <div className="space-y-4">
      <aside role="note" aria-label={isPt ? 'Limites do mapa orbital' : 'Orbital map limitations'} className="rounded-xl border border-amber-700/60 bg-amber-950/20 px-4 py-3 text-sm leading-relaxed text-amber-100">
        <p>{isPt
          ? 'Visualização exploratória, não reconstrução de queda: posições, horários do cursor e faixas são resultados de modelo, não medições terminais. A NASA registrou apenas o dia 8/11/1963 para o decaimento do 528; hora e local não estão determinados. Marcos ilustrativos ocultos por padrão.'
          : 'Exploratory visualization, not a crash reconstruction: cursor times, positions and bands are model outputs, not terminal measurements. NASA records only November 8, 1963 as the decay date for 528; time and location are undetermined. Illustrative markers are hidden by default.'}</p>
        <p className="mt-2 flex flex-wrap gap-x-5 gap-y-2">
          <a className="text-cyan-200 underline underline-offset-4 focus-visible:outline" href="#/research/c197">{isPt ? 'C197–C202: NASA e limite da data' : 'C197–C202: NASA date evidence'}</a>
          <a className="text-cyan-200 underline underline-offset-4 focus-visible:outline" href="#/research/raan">{isPt ? 'Conflito RAAN e proveniência' : 'RAAN and provenance conflict'}</a>
        </p>
      </aside>
      {/* Top Map Toolbar */}
      <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-3 flex flex-wrap items-center justify-between gap-3 text-xs">
        {/* Left: Mode toggles */}
        <div className="flex items-center gap-2 flex-wrap">
          <div className="flex bg-zinc-950 p-1 rounded-lg border border-zinc-800">
            <button
              onClick={() => setMapMode('google-earth')}
              className={`flex items-center gap-1.5 px-3 py-1 rounded text-xs font-semibold cursor-pointer transition-colors ${
                mapMode === 'google-earth'
                  ? 'bg-cyan-600 text-white shadow'
                  : 'text-zinc-400 hover:text-zinc-200'
              }`}
            >
              <SatelliteIcon className="w-3.5 h-3.5 text-cyan-200" />
              <span>Google Earth / Satélite</span>
            </button>
            <button
              onClick={() => setMapMode('2D')}
              className={`flex items-center gap-1.5 px-3 py-1 rounded text-xs font-medium cursor-pointer transition-colors ${
                mapMode === '2D' ? 'bg-cyan-600 text-white' : 'text-zinc-400 hover:text-zinc-200'
              }`}
            >
              <MapIcon className="w-3.5 h-3.5" />
              <span>Plano 2D</span>
            </button>
            <button
              onClick={() => setMapMode('3D')}
              className={`flex items-center gap-1.5 px-3 py-1 rounded text-xs font-medium cursor-pointer transition-colors ${
                mapMode === '3D' ? 'bg-cyan-600 text-white' : 'text-zinc-400 hover:text-zinc-200'
              }`}
            >
              <Globe2 className="w-3.5 h-3.5" />
              <span>Globo 3D</span>
            </button>
          </div>

          <label className="flex items-center gap-1.5 px-2.5 py-1.5 rounded bg-zinc-950 border border-zinc-800 text-zinc-300 cursor-pointer select-none">
            <input
              type="checkbox"
              checked={showSisterSatellites}
              onChange={(e) => setShowSisterSatellites(e.target.checked)}
              className="accent-cyan-500 rounded"
            />
            <span className="font-mono text-[11px]">3 Objetos</span>
          </label>

          <label className="flex items-center gap-1.5 px-2.5 py-1.5 rounded bg-cyan-950/40 border border-cyan-800/80 text-cyan-300 cursor-pointer select-none">
            <input
              type="checkbox"
              checked={showUncertaintyBuffer}
              onChange={(e) => setShowUncertaintyBuffer(e.target.checked)}
              className="accent-cyan-400 rounded"
            />
            <span className="font-mono text-[11px] flex items-center gap-1">
              <Compass className="w-3 h-3 text-cyan-400" />
              <span>Faixa sintética (não calibrada)</span>
            </span>
          </label>

          <label className="flex items-center gap-1.5 px-2.5 py-1.5 rounded bg-cyan-950/60 border border-cyan-800 text-cyan-300 cursor-pointer select-none font-mono text-[11px]">
            <input
              type="checkbox"
              checked={pauseOnObservations}
              onChange={(e) => setPauseOnObservations(e.target.checked)}
              className="accent-cyan-400 rounded"
            />
            <span className="flex items-center gap-1">
              <Radio className="w-3 h-3 text-cyan-400 animate-pulse" />
              <span>Pausar em marcos simulados</span>
            </span>
          </label>

          <label className="flex items-center gap-1.5 px-2.5 py-1.5 rounded bg-cyan-950/70 border border-cyan-700 text-cyan-200 cursor-pointer select-none font-mono text-[11px]">
            <input
              type="checkbox"
              checked={showObservationMarkers}
              onChange={(e) => setShowObservationMarkers(e.target.checked)}
              className="accent-cyan-400 rounded"
            />
            <span className="flex items-center gap-1">
              <Anchor className="w-3.5 h-3.5 text-cyan-400" />
              <span>Marcos ilustrativos ({noradObservationMarkers.length})</span>
            </span>
          </label>

          <button
            onClick={() => setShowAnchorsListDrawer(!showAnchorsListDrawer)}
            className={`flex items-center gap-1.5 px-2.5 py-1.5 rounded text-[11px] font-mono cursor-pointer transition-colors border ${
              showAnchorsListDrawer
                ? 'bg-cyan-600 border-cyan-400 text-white font-bold shadow-md'
                : 'bg-zinc-950 border-zinc-800 hover:bg-zinc-800 text-zinc-300'
            }`}
            title="Abrir painel com as 11 medições históricas que amarram a trajetória"
          >
            <ListFilter className="w-3.5 h-3.5 text-cyan-400" />
            <span>Medições (11)</span>
          </button>

          <label className="flex items-center gap-1.5 px-2.5 py-1.5 rounded bg-emerald-950/60 border border-emerald-700/80 text-emerald-200 cursor-pointer select-none font-mono text-[11px]">
            <input
              type="checkbox"
              checked={showInterTrackVectors}
              onChange={(e) => setShowInterTrackVectors(e.target.checked)}
              className="accent-emerald-400 rounded"
            />
            <span className="flex items-center gap-1">
              <GitCommit className="w-3.5 h-3.5 text-emerald-400" />
              <span>Trajetória Passada/Futura (527 & 529)</span>
            </span>
          </label>
        </div>

        {/* Right: Camera Focus & NORAD Stepper */}
        <div className="flex items-center gap-2 flex-wrap">
          {mapMode === 'google-earth' && (
            <div className="flex items-center gap-1.5 mr-2">
              <button
                onClick={centerOnConde}
                className="px-2.5 py-1 rounded bg-rose-950/80 border border-rose-800 hover:bg-rose-900 text-rose-300 font-mono text-[11px] flex items-center gap-1 cursor-pointer"
                title="Focar na Região de Conde, BA"
              >
                <Crosshair className="w-3.5 h-3.5 text-rose-400" />
                <span>Ver Conde</span>
              </button>
              <button
                onClick={centerOn528}
                className={`px-2.5 py-1 rounded font-mono text-[11px] flex items-center gap-1 cursor-pointer transition-colors ${
                  followSatellite
                    ? 'bg-cyan-600 text-white font-bold'
                    : 'bg-zinc-800 hover:bg-zinc-700 text-cyan-300 border border-zinc-700'
                }`}
                title="Seguir Satélite NORAD 528 na Câmera"
              >
                <SatelliteIcon className="w-3.5 h-3.5 text-cyan-400" />
                <span>{followSatellite ? 'Seguindo 528' : 'Focar 528'}</span>
              </button>
            </div>
          )}

          <button
            onClick={() => stepObservation('prev')}
            className="px-2.5 py-1 rounded bg-zinc-800 hover:bg-zinc-700 text-zinc-300 font-mono text-[11px] flex items-center gap-1 cursor-pointer"
            title="Marco exploratório anterior"
          >
            <ChevronLeft className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Marco anterior</span>
          </button>

          <select
            value={currentObsIndex}
            onChange={(e) => {
              const idx = Number(e.target.value);
              const ev = displayedMilestones[idx];
              setIsPlaying(false);
              jumpToTime(ev.timestampMs, ev);
            }}
            className="bg-zinc-950 border border-zinc-800 text-cyan-300 text-xs rounded-lg px-2.5 py-1 font-mono cursor-pointer max-w-[200px] sm:max-w-[260px] truncate"
          >
            {displayedMilestones.map((ev, i) => (
              <option key={ev.id} value={i}>
                #{ev.order} ({ev.utcString.substring(0, 10)}): {ev.titlePt}
              </option>
            ))}
          </select>

          <button
            onClick={() => stepObservation('next')}
            className="px-2.5 py-1 rounded bg-cyan-950 border border-cyan-700 text-cyan-300 font-mono text-[11px] flex items-center gap-1 cursor-pointer font-semibold hover:bg-cyan-900"
            title="Próximo marco exploratório"
          >
            <span className="hidden sm:inline">Próx. marco</span>
            <ChevronRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Main Map Visualizer Display */}
      <div className="relative bg-zinc-950 border border-zinc-800 rounded-xl overflow-hidden shadow-2xl h-[520px] w-full">
        {mapMode === 'google-earth' ? (
          <APIProvider apiKey={mapsApiKey}>
            <GoogleMap
              center={gmapCenter}
              zoom={gmapZoom}
              onCameraChanged={(ev) => {
                setGmapCenter(ev.detail.center);
                setGmapZoom(ev.detail.zoom);
              }}
              mapTypeId="hybrid"
              mapId="DEMO_MAP_ID"
              gestureHandling="greedy"
              disableDefaultUI={false}
              internalUsageAttributionIds={['gmp_mcp_codeassist_v1_aistudio']}
              className="w-full h-full"
            >
              {/* Conde, Bahia Ground Target Pin & Radius Rings */}
              <AdvancedMarker
                position={{
                  lat: CONDE_COORDINATES.latitude,
                  lng: CONDE_COORDINATES.longitude,
                }}
                onClick={() => setSelectedPinSatellite('conde')}
              >
                <div className="relative flex items-center justify-center cursor-pointer group">
                  <div className="absolute w-6 h-6 rounded-full bg-rose-500/40 animate-ping" />
                  <div className="relative px-2 py-1 rounded bg-rose-950 border-2 border-rose-500 text-rose-100 font-bold text-[11px] flex items-center gap-1 shadow-xl">
                    <Crosshair className="w-3.5 h-3.5 text-rose-400" />
                    <span>CONDE, BA</span>
                  </div>
                </div>
              </AdvancedMarker>

              {/* Conde Radar Horizon Rings (100 km, 250 km, 500 km) */}
              {showHorizonMasks && (
                <>
                  <GoogleCircle
                    center={{
                      lat: CONDE_COORDINATES.latitude,
                      lng: CONDE_COORDINATES.longitude,
                    }}
                    radius={100000} // 100 km
                    strokeColor="#f43f5e"
                    strokeWeight={2}
                    fillColor="#f43f5e"
                    fillOpacity={0.15}
                  />
                  <GoogleCircle
                    center={{
                      lat: CONDE_COORDINATES.latitude,
                      lng: CONDE_COORDINATES.longitude,
                    }}
                    radius={250000} // 250 km
                    strokeColor="#fb7185"
                    strokeWeight={1.5}
                    strokeOpacity={0.6}
                    fillColor="#f43f5e"
                    fillOpacity={0.06}
                  />
                  <GoogleCircle
                    center={{
                      lat: CONDE_COORDINATES.latitude,
                      lng: CONDE_COORDINATES.longitude,
                    }}
                    radius={500000} // 500 km
                    strokeColor="#fca5a5"
                    strokeWeight={1}
                    strokeOpacity={0.4}
                    fillColor="#f43f5e"
                    fillOpacity={0.02}
                  />
                </>
              )}

              {/* Ground Tracks on Google Satellite (split by antimeridian) */}
              {/* NORAD 527 (OPS 0180) track in Emerald */}
              {showSisterSatellites &&
                googleTrack527Segments.map((seg, idx) => (
                  <GooglePolyline
                    key={`track527-${idx}`}
                    path={seg}
                    strokeColor="#10b981"
                    strokeOpacity={0.8}
                    strokeWeight={2}
                  />
                ))}

              {/* NORAD 529 track in Purple */}
              {showSisterSatellites &&
                googleTrack529Segments.map((seg, idx) => (
                  <GooglePolyline
                    key={`track529-${idx}`}
                    path={seg}
                    strokeColor="#c084fc"
                    strokeOpacity={0.8}
                    strokeWeight={2}
                  />
                ))}

              {/* Uncalibrated illustrative band for NORAD 528 */}
              {showUncertaintyBuffer && (
                <>
                  {googleUncertaintyRails.leftSegments.map((seg, idx) => (
                    <GooglePolyline
                      key={`rail-left-${idx}`}
                      path={seg}
                      strokeColor="#22d3ee"
                      strokeOpacity={0.45}
                      strokeWeight={1.5}
                    />
                  ))}
                  {googleUncertaintyRails.rightSegments.map((seg, idx) => (
                    <GooglePolyline
                      key={`rail-right-${idx}`}
                      path={seg}
                      strokeColor="#22d3ee"
                      strokeOpacity={0.45}
                      strokeWeight={1.5}
                    />
                  ))}
                </>
              )}

              {/* NORAD 528 (Target) track in Cyan */}
              {googleTrack528Segments.map((seg, idx) => (
                <GooglePolyline
                  key={`track528-${idx}`}
                  path={seg}
                  strokeColor="#06b6d4"
                  strokeOpacity={0.95}
                  strokeWeight={3.5}
                />
              ))}

              {/* Satellite Markers */}
              {/* NORAD 527 (OPS 0180) Marker */}
              {sat527Point && showSisterSatellites && (
                <AdvancedMarker
                  position={{
                    lat: sat527Point.latitude,
                    lng: sat527Point.longitude,
                  }}
                  onClick={() => setSelectedPinSatellite('527')}
                >
                  <div className="bg-emerald-950/90 border border-emerald-500 rounded px-1.5 py-0.5 text-[10px] font-mono text-emerald-200 flex items-center gap-1 shadow-lg cursor-pointer hover:bg-emerald-900">
                    <span className="w-2 h-2 rounded-full bg-emerald-400" />
                    <span>527 [{sat527Point.altitudeKm.toFixed(0)} km]</span>
                  </div>
                </AdvancedMarker>
              )}

              {/* NORAD 529 Marker */}
              {sat529Point && showSisterSatellites && (
                <AdvancedMarker
                  position={{
                    lat: sat529Point.latitude,
                    lng: sat529Point.longitude,
                  }}
                  onClick={() => setSelectedPinSatellite('529')}
                >
                  <div className="bg-purple-950/90 border border-purple-500 rounded px-1.5 py-0.5 text-[10px] font-mono text-purple-200 flex items-center gap-1 shadow-lg cursor-pointer hover:bg-purple-900">
                    <span className="w-2 h-2 rounded-full bg-purple-400" />
                    <span>529 [{sat529Point.altitudeKm.toFixed(0)} km]</span>
                  </div>
                </AdvancedMarker>
              )}

              {/* NORAD 528 Target Satellite Marker */}
              {sat528Point && (
                <AdvancedMarker
                  position={{
                    lat: sat528Point.latitude,
                    lng: sat528Point.longitude,
                  }}
                  onClick={() => setSelectedPinSatellite('528')}
                >
                  <div className="relative flex flex-col items-center cursor-pointer">
                    <div className="absolute -top-1 w-7 h-7 rounded-full bg-cyan-400/40 animate-ping" />
                    <div className="relative px-2 py-1 rounded-lg bg-cyan-950 border-2 border-cyan-400 text-cyan-100 font-mono font-bold text-xs flex items-center gap-1.5 shadow-2xl">
                      <SatelliteIcon className="w-3.5 h-3.5 text-cyan-300 animate-spin" />
                      <span>NORAD 528</span>
                      <span className="text-[10px] text-cyan-300">
                        {sat528Point.altitudeKm.toFixed(0)} km
                      </span>
                    </div>
                  </div>
                </AdvancedMarker>
              )}

              {/* Inter-Track Proximity Vectors (Past & Future Passes of 527 and 529) */}
              {showInterTrackVectors && sat528Point && interTrackData && (
                <>
                  {/* Connector line to 527 Past Pass */}
                  <GooglePolyline
                    path={[
                      { lat: sat528Point.latitude, lng: sat528Point.longitude },
                      { lat: interTrackData.past527.latitude, lng: interTrackData.past527.longitude },
                    ]}
                    strokeColor="#10b981"
                    strokeOpacity={0.75}
                    strokeWeight={2}
                  />

                  {/* Connector line to 527 Future Pass */}
                  <GooglePolyline
                    path={[
                      { lat: sat528Point.latitude, lng: sat528Point.longitude },
                      { lat: interTrackData.future527.latitude, lng: interTrackData.future527.longitude },
                    ]}
                    strokeColor="#34d399"
                    strokeOpacity={0.75}
                    strokeWeight={2}
                  />

                  {/* Connector line to 529 Past Pass */}
                  <GooglePolyline
                    path={[
                      { lat: sat528Point.latitude, lng: sat528Point.longitude },
                      { lat: interTrackData.past529.latitude, lng: interTrackData.past529.longitude },
                    ]}
                    strokeColor="#c084fc"
                    strokeOpacity={0.75}
                    strokeWeight={2}
                  />

                  {/* Connector line to 529 Future Pass */}
                  <GooglePolyline
                    path={[
                      { lat: sat528Point.latitude, lng: sat528Point.longitude },
                      { lat: interTrackData.future529.latitude, lng: interTrackData.future529.longitude },
                    ]}
                    strokeColor="#a855f7"
                    strokeOpacity={0.75}
                    strokeWeight={2}
                  />

                  {/* Marker for 527 Past Pass Point */}
                  <AdvancedMarker
                    position={{
                      lat: interTrackData.past527.latitude,
                      lng: interTrackData.past527.longitude,
                    }}
                    title={`527 Passagem Passada: há ${Math.abs(interTrackData.past527.deltaMinutes)} min (${interTrackData.past527.distanceKm} km)`}
                  >
                    <div className="bg-emerald-950/90 border border-emerald-400 rounded px-1.5 py-0.5 text-[9px] font-mono text-emerald-200 shadow-md flex items-center gap-1 select-none">
                      <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
                      <span>527 Passada ({interTrackData.past527.deltaMinutes}m): {interTrackData.past527.distanceKm} km</span>
                    </div>
                  </AdvancedMarker>

                  {/* Marker for 527 Future Pass Point */}
                  <AdvancedMarker
                    position={{
                      lat: interTrackData.future527.latitude,
                      lng: interTrackData.future527.longitude,
                    }}
                    title={`527 Próxima Passagem: em +${interTrackData.future527.deltaMinutes} min (${interTrackData.future527.distanceKm} km)`}
                  >
                    <div className="bg-emerald-950/90 border border-emerald-300 rounded px-1.5 py-0.5 text-[9px] font-mono text-emerald-100 shadow-md flex items-center gap-1 select-none">
                      <span className="w-1.5 h-1.5 rounded-full bg-emerald-300" />
                      <span>527 Futura (+{interTrackData.future527.deltaMinutes}m): {interTrackData.future527.distanceKm} km</span>
                    </div>
                  </AdvancedMarker>

                  {/* Marker for 529 Past Pass Point */}
                  <AdvancedMarker
                    position={{
                      lat: interTrackData.past529.latitude,
                      lng: interTrackData.past529.longitude,
                    }}
                    title={`529 Passagem Passada: há ${Math.abs(interTrackData.past529.deltaMinutes)} min (${interTrackData.past529.distanceKm} km)`}
                  >
                    <div className="bg-purple-950/90 border border-purple-400 rounded px-1.5 py-0.5 text-[9px] font-mono text-purple-200 shadow-md flex items-center gap-1 select-none">
                      <span className="w-1.5 h-1.5 rounded-full bg-purple-400" />
                      <span>529 Passada ({interTrackData.past529.deltaMinutes}m): {interTrackData.past529.distanceKm} km</span>
                    </div>
                  </AdvancedMarker>

                  {/* Marker for 529 Future Pass Point */}
                  <AdvancedMarker
                    position={{
                      lat: interTrackData.future529.latitude,
                      lng: interTrackData.future529.longitude,
                    }}
                    title={`529 Próxima Passagem: em +${interTrackData.future529.deltaMinutes} min (${interTrackData.future529.distanceKm} km)`}
                  >
                    <div className="bg-purple-950/90 border border-purple-300 rounded px-1.5 py-0.5 text-[9px] font-mono text-purple-100 shadow-md flex items-center gap-1 select-none">
                      <span className="w-1.5 h-1.5 rounded-full bg-purple-300" />
                      <span>529 Futura (+{interTrackData.future529.deltaMinutes}m): {interTrackData.future529.distanceKm} km</span>
                    </div>
                  </AdvancedMarker>
                </>
              )}

              {/* Illustrative model milestones: never claimed as radar fixes */}
              {showObservationMarkers &&
                noradObservationMarkers.map((marker) => {
                  const isCurrent = marker.isCurrent;
                  const is527 =
                    marker.event.focalObject === 527 ||
                    marker.event.id === 'OBS-05' ||
                    marker.event.id === 'OBS-09';
                  const is529 =
                    marker.event.focalObject === 529 ||
                    marker.event.id === 'OBS-10';

                  let badgeStyle = 'bg-cyan-950/95 border-cyan-400 text-cyan-200';
                  let dotStyle = 'bg-cyan-400';
                  if (is527) {
                    badgeStyle = 'bg-emerald-950/95 border-emerald-400 text-emerald-200';
                    dotStyle = 'bg-emerald-400';
                  } else if (is529) {
                    badgeStyle = 'bg-purple-950/95 border-purple-400 text-purple-200';
                    dotStyle = 'bg-purple-400';
                  }

                  return (
                    <AdvancedMarker
                      key={`gmap-obs-${marker.event.id}`}
                      position={marker.position}
                      onClick={() => {
                        setIsPlaying(false);
                        jumpToTime(marker.event.timestampMs, marker.event);
                        setSelectedObsMarker(marker);
                        setGmapCenter(marker.position);
                        if (gmapZoom < 5) setGmapZoom(5);
                      }}
                      title={`#${marker.event.order}: ${marker.event.titlePt} (${marker.event.utcString})`}
                    >
                      <div className="relative flex flex-col items-center cursor-pointer group select-none">
                        {isCurrent && (
                          <div className="absolute -top-1 w-9 h-9 rounded-full bg-amber-400/50 animate-ping pointer-events-none" />
                        )}

                        <div
                          className={`px-2 py-0.5 rounded-md border text-[11px] font-mono font-bold shadow-2xl flex items-center gap-1.5 transition-all duration-150 ${badgeStyle} ${
                            isCurrent
                              ? 'scale-115 ring-2 ring-white shadow-2xl brightness-125'
                              : 'hover:scale-110 hover:brightness-125'
                          }`}
                        >
                          <span
                            className={`w-2 h-2 rounded-full ${dotStyle} ${
                              isCurrent ? 'animate-pulse' : ''
                            }`}
                          />
                          <span className="font-extrabold text-white">#{marker.event.order}</span>
                          <span className="text-[10px] hidden sm:inline-block max-w-[130px] truncate">
                            {marker.shortLabel}
                          </span>
                        </div>

                        {/* Coords & Altitude tag */}
                        <div className="mt-0.5 px-1 py-0.2 rounded bg-black/85 text-[9px] font-mono text-zinc-300 border border-zinc-700/80 shadow flex items-center gap-1">
                          <span className="text-cyan-300">{marker.altitudeKm.toFixed(0)} km</span>
                          <span className="text-zinc-500">|</span>
                          <span>{marker.event.utcString.substring(5, 10)}</span>
                        </div>
                      </div>
                    </AdvancedMarker>
                  );
                })}

              {/* InfoWindow for Clicked Observation Marker */}
              {selectedObsMarker && (
                <InfoWindow
                  position={selectedObsMarker.position}
                  onCloseClick={() => setSelectedObsMarker(null)}
                >
                  <div className="bg-zinc-950 text-zinc-100 p-2.5 rounded-lg max-w-xs space-y-2 font-sans border border-cyan-800/80 shadow-2xl">
                    <div className="flex items-center justify-between border-b border-zinc-800 pb-1.5">
                      <div className="flex items-center gap-1.5">
                        <span className="px-1.5 py-0.5 rounded bg-cyan-950 border border-cyan-500 text-cyan-300 font-mono font-bold text-[10px]">
                          NORAD #{selectedObsMarker.event.order}
                        </span>
                        <span className="text-[10px] text-zinc-400 font-mono">
                          {selectedObsMarker.event.utcString.substring(0, 10)}
                        </span>
                      </div>
                    </div>

                    <h4 className="text-xs font-bold text-zinc-100 leading-snug">
                      {isPt ? selectedObsMarker.event.titlePt : selectedObsMarker.event.titleEn}
                    </h4>

                    <div className="space-y-1 text-[10px] font-mono text-zinc-300 bg-zinc-900/90 p-2 rounded border border-zinc-800">
                      <div className="flex justify-between">
                        <span className="text-zinc-400">Hora do modelo:</span>
                        <span className="text-cyan-300 font-bold">
                          {selectedObsMarker.event.utcString.substring(11, 19)} UTC
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-zinc-400">Conversão Bahia:</span>
                        <span className="text-zinc-200">{selectedObsMarker.event.localTimeString}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-zinc-400">Posição ilustrativa:</span>
                        <span className="text-amber-300">{selectedObsMarker.formattedCoord}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-zinc-400">Altitude:</span>
                        <span className="text-emerald-300 font-bold">~{selectedObsMarker.altitudeKm.toFixed(0)} km</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-zinc-400">Distância a Conde:</span>
                        <span className="text-rose-300 font-bold">~{selectedObsMarker.distanceToCondeKm.toLocaleString()} km</span>
                      </div>
                      <div className="pt-1 text-[9px] text-zinc-400 border-t border-zinc-800 truncate">
                        <span className="text-zinc-500">Estação: </span>
                        {selectedObsMarker.trackingStation}
                      </div>
                    </div>

                    <div className="flex items-center gap-1.5 pt-1">
                      <button
                        onClick={() => {
                          jumpToTime(selectedObsMarker.event.timestampMs, selectedObsMarker.event);
                          setSelectedObsMarker(null);
                        }}
                        className="w-full py-1 rounded bg-cyan-600 hover:bg-cyan-500 text-white font-mono text-[10px] font-bold text-center cursor-pointer transition-colors"
                      >
                        Ver contexto da simulação
                      </button>
                    </div>
                  </div>
                </InfoWindow>
              )}
            </GoogleMap>
          </APIProvider>
        ) : (
          <canvas
            ref={canvasRef}
            width={1040}
            height={520}
            onMouseDown={handleMouseDown}
            onMouseMove={handleMouseMove}
            onMouseUp={handleMouseUp}
            className="w-full h-full cursor-crosshair block select-none"
          />
        )}

        {/* Active NORAD Observation Event Overlay Drawer / Banner */}
        {activeObservationModal && (
          <div className="absolute top-3 left-3 right-3 sm:right-auto sm:max-w-lg bg-zinc-950/95 backdrop-blur-md border border-cyan-800/80 rounded-xl p-4 shadow-2xl space-y-3 z-30 animate-in fade-in duration-200">
            <div className="flex items-start justify-between gap-2 border-b border-zinc-800 pb-2">
              <div className="space-y-0.5">
                <div className="flex items-center gap-2">
                  <span className="px-2 py-0.5 rounded bg-cyan-950 border border-cyan-700 text-cyan-300 font-mono font-bold text-[10px]">
                    MARCO DE SIMULAÇÃO #{activeObservationModal.order}
                  </span>
                  <span className="text-zinc-500 font-mono text-[10px]">|</span>
                  <span className="text-[10px] text-zinc-400 font-mono">
                    {activeObservationModal.authority}
                  </span>
                </div>
                <h4 className="text-sm font-bold text-zinc-100">
                  {isPt ? activeObservationModal.titlePt : activeObservationModal.titleEn}
                </h4>
              </div>
              <button
                onClick={() => setActiveObservationModal(null)}
                className="text-zinc-400 hover:text-zinc-200 p-1 rounded cursor-pointer"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="text-xs text-zinc-300 space-y-2">
              <div className="flex items-center gap-2 text-[11px] font-mono text-cyan-400">
                <Clock className="w-3.5 h-3.5 text-cyan-400" />
                <span>{activeObservationModal.utcString}</span>
                <span className="text-zinc-500">•</span>
                <span className="text-zinc-400">{activeObservationModal.localTimeString}</span>
              </div>

              <p className="text-[11px] text-zinc-300 leading-relaxed">
                {isPt ? activeObservationModal.descriptionPt : activeObservationModal.descriptionEn}
              </p>

              {/* Status of All 3 Objects at this Observation */}
              <div className="p-2.5 rounded-lg bg-zinc-900 border border-zinc-800/80 space-y-1 font-mono text-[10px]">
                <div className="text-zinc-400 uppercase tracking-wider font-bold text-[9px] mb-1">
                  Estado do modelo (3 corpos):
                </div>
                <div className="flex justify-between text-cyan-300">
                  <span>NORAD 528 (Alvo):</span>
                  <span className="font-bold">{activeObservationModal.status528}</span>
                </div>
                <div className="flex justify-between text-emerald-400">
                  <span>NORAD 527 (OPS 0180):</span>
                  <span>{activeObservationModal.status527}</span>
                </div>
                <div className="flex justify-between text-purple-300">
                  <span>NORAD 529 (Comp. C):</span>
                  <span>{activeObservationModal.status529}</span>
                </div>
              </div>
            </div>

            <div className="flex items-center justify-between pt-1 border-t border-zinc-900 text-xs">
              <button
                onClick={() => {
                  setActiveObservationModal(null);
                  setIsPlaying(true);
                }}
                className="px-3 py-1.5 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white font-medium text-xs flex items-center gap-1.5 cursor-pointer shadow"
              >
                <Play className="w-3.5 h-3.5" />
                <span>Continuar Reprodução</span>
              </button>

              <button
                onClick={() => stepObservation('next')}
                className="px-3 py-1.5 rounded-lg bg-zinc-800 hover:bg-zinc-700 text-zinc-300 text-xs flex items-center gap-1.5 cursor-pointer font-mono"
              >
                <span>Próxima Obs.</span>
                <ChevronRight className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        )}

        {/* NORAD 11 Benchmark Observations Slide-Over / Overlay Drawer */}
        {showAnchorsListDrawer && (
          <div className="absolute top-3 right-3 bottom-3 w-full sm:w-[460px] max-w-[94%] bg-zinc-950/95 backdrop-blur-md border border-cyan-800 rounded-xl p-4 shadow-2xl z-30 flex flex-col space-y-3 animate-in fade-in slide-in-from-right duration-200">
            {/* Header */}
            <div className="flex items-start justify-between border-b border-zinc-800 pb-2.5">
              <div className="space-y-0.5">
                <div className="flex items-center gap-1.5 text-cyan-400 font-mono text-xs font-bold">
                  <Anchor className="w-4 h-4 text-cyan-400" />
                  <span>MARCOS DE SIMULAÇÃO (NÃO MEDIÇÕES)</span>
                </div>
                <p className="text-[11px] text-zinc-400 leading-tight">
                  Tempos e posições ilustrativos, sem comprovação de medição radar nesses pontos. Não usar como trajetória terminal.
                </p>
              </div>
              <button
                onClick={() => setShowAnchorsListDrawer(false)}
                className="text-zinc-400 hover:text-zinc-200 p-1 rounded hover:bg-zinc-800 cursor-pointer"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* List of 11 Measurements */}
            <div className="flex-1 overflow-y-auto space-y-2 pr-1 custom-scrollbar">
              {noradObservationMarkers.map((marker) => {
                const isCurrent = marker.isCurrent;
                const is527 =
                  marker.event.focalObject === 527 ||
                  marker.event.id === 'OBS-05' ||
                  marker.event.id === 'OBS-09';
                const is529 =
                  marker.event.focalObject === 529 ||
                  marker.event.id === 'OBS-10';

                let borderStyle = 'border-zinc-800 hover:border-cyan-700 bg-zinc-900/70';
                let badgeStyle = 'bg-cyan-950 text-cyan-300 border-cyan-700';
                if (isCurrent) {
                  borderStyle = 'border-amber-500 bg-amber-950/30 ring-1 ring-amber-500';
                  badgeStyle = 'bg-amber-950 text-amber-200 border-amber-500 font-bold';
                } else if (is527) {
                  borderStyle = 'border-emerald-900/80 hover:border-emerald-600 bg-emerald-950/20';
                  badgeStyle = 'bg-emerald-950 text-emerald-300 border-emerald-700';
                } else if (is529) {
                  borderStyle = 'border-purple-900/80 hover:border-purple-600 bg-purple-950/20';
                  badgeStyle = 'bg-purple-950 text-purple-300 border-purple-700';
                }

                return (
                  <div
                    key={marker.event.id}
                    className={`p-2.5 rounded-lg border transition-all ${borderStyle} text-xs space-y-1.5`}
                  >
                    <div className="flex items-center justify-between gap-1">
                      <div className="flex items-center gap-1.5">
                        <span className={`px-1.5 py-0.5 rounded font-mono text-[10px] border ${badgeStyle}`}>
                          #{marker.event.order}
                        </span>
                        <span className="font-mono text-[10px] text-zinc-300 font-bold">
                          {marker.event.utcString.substring(0, 10)}
                        </span>
                      </div>
                      <span className="font-mono text-[10px] text-zinc-400">
                        {marker.event.utcString.substring(11, 16)} UTC ({marker.event.localTimeString.substring(0, 5)} BA)
                      </span>
                    </div>

                    <div className="font-bold text-zinc-200 leading-snug">
                      {isPt ? marker.event.titlePt : marker.event.titleEn}
                    </div>

                    {/* Model positions, not original radar observations */}
                    <div className="grid grid-cols-2 gap-1 text-[10px] font-mono bg-zinc-950/80 p-1.5 rounded border border-zinc-800/80">
                      <div>
                        <span className="text-zinc-500">Coord: </span>
                        <span className="text-amber-300 font-semibold">{marker.formattedCoord}</span>
                      </div>
                      <div>
                        <span className="text-zinc-500">Altitude: </span>
                        <span className="text-emerald-400 font-semibold">~{marker.altitudeKm.toFixed(0)} km</span>
                      </div>
                      <div className="col-span-2 flex justify-between text-zinc-400">
                        <span>Dist. Conde: <strong className="text-rose-400">~{marker.distanceToCondeKm.toLocaleString()} km</strong></span>
                        <span className="text-zinc-500 truncate max-w-[170px]" title={marker.trackingStation}>
                          {marker.trackingStation}
                        </span>
                      </div>
                    </div>

                    <div className="flex items-center justify-between pt-1">
                      <span className="text-[10px] text-zinc-400 font-mono truncate max-w-[200px]">
                        528: <span className="text-cyan-300 font-semibold">{marker.event.status528.substring(0, 28)}</span>
                      </span>

                      <button
                        onClick={() => {
                          setIsPlaying(false);
                          jumpToTime(marker.event.timestampMs, marker.event);
                          setSelectedObsMarker(marker);
                          if (mapMode === 'google-earth') {
                            setGmapCenter(marker.position);
                            setGmapZoom(6);
                          }
                        }}
                        className="px-2 py-1 rounded bg-cyan-900/60 hover:bg-cyan-800 text-cyan-200 border border-cyan-700/80 font-mono text-[10px] flex items-center gap-1 cursor-pointer transition-colors"
                      >
                        <Crosshair className="w-3 h-3 text-cyan-300" />
                        <span>Focar e Simular</span>
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Footer Summary */}
            <div className="pt-2 border-t border-zinc-800 flex items-center justify-between text-[11px] font-mono text-zinc-400">
              <span>Marcos ilustrativos: {displayedMilestones.length}</span>
              <button
                onClick={() => {
                  setShowAnchorsListDrawer(false);
                  setIsPlaying(true);
                }}
                className="text-cyan-400 hover:text-cyan-300 font-semibold cursor-pointer"
              >
                Retomar Simulação →
              </button>
            </div>
          </div>
        )}

        {/* Telemetry Overlay Card */}
        <div className="absolute bottom-3 left-3 bg-zinc-950/85 backdrop-blur border border-zinc-800 rounded-lg p-3 text-xs font-mono text-zinc-300 space-y-1.5 max-w-sm pointer-events-none shadow-lg z-20">
          <div className="flex items-center justify-between border-b border-zinc-800 pb-1 text-cyan-400 font-bold">
            <span>SISTEMA ORBITAL 1963-003</span>
            <span className="text-[10px] text-zinc-500 font-mono">
              {isBeforeLaunch
                ? 'PRÉ-LANÇAMENTO'
                : is528Decayed
                ? '528 DECAÍDO'
                : '3 OBJETOS RASTREADOS'}
            </span>
          </div>

          <div className="space-y-1 text-[11px]">
            {/* 528 */}
            <div className="flex justify-between items-center text-cyan-300">
              <span>NORAD 528 (Alvo):</span>
              <span className="font-bold">
                {isBeforeLaunch
                  ? 'Aguardando Lançamento'
                  : is528Decayed
                  ? 'Decaído (08/11/1963)'
                  : sat528Point
                  ? `${sat528Point.altitudeKm.toFixed(0)} km | ${sat528Point.distanceToCondeKm.toFixed(0)} km de Conde`
                  : 'Rastreado'}
              </span>
            </div>

            {/* Incerteza TLE Dinâmica */}
            {!isBeforeLaunch && !is528Decayed && envelopes528.length > 0 && (
              <div className="flex justify-between items-center text-cyan-400/80 text-[10px] bg-cyan-950/40 px-1.5 py-0.5 rounded border border-cyan-800/40">
                <span>Incerteza TLE (±1σ):</span>
                <span className="font-bold">
                  {`±${envelopes528[Math.floor(envelopes528.length / 2)]?.crossTrackKm.toFixed(0)} km cross / ±${envelopes528[Math.floor(envelopes528.length / 2)]?.alongTrackKm.toFixed(0)} km along`}
                </span>
              </div>
            )}

            {/* Distância Relativa Instantânea 528 <-> 527 (Triangulação Dinâmica) */}
            {sat528Point && sat527Point && !is528Decayed && (
              <div className="flex justify-between items-center text-emerald-300 text-[10px] bg-emerald-950/30 px-1.5 py-0.5 rounded border border-emerald-800/40">
                <span>Distância Relativa 528 ↔ 527:</span>
                <span className="font-bold font-mono">
                  {Math.round(
                    Math.hypot(
                      (sat528Point.latitude - sat527Point.latitude) * 111,
                      (sat528Point.longitude - sat527Point.longitude) * 111 * Math.cos((sat528Point.latitude * Math.PI) / 180),
                      sat528Point.altitudeKm - sat527Point.altitudeKm
                    )
                  ).toLocaleString()}{' '}
                  km
                </span>
              </div>
            )}

            {/* Distâncias às Trajetórias Passada e Futura do 527 e 529 */}
            {interTrackData && showInterTrackVectors && !is528Decayed && (
              <div className="space-y-1 pt-1 border-t border-zinc-800 text-[10px]">
                <div className="text-zinc-400 font-bold uppercase text-[9px] flex items-center justify-between">
                  <span>Enquadramento de Trajetórias:</span>
                  <span className="text-emerald-300 font-mono">
                    Corredor ~{interTrackData.corridorWidth527Km.toLocaleString()} km
                  </span>
                </div>
                <div className="flex justify-between text-emerald-300 bg-emerald-950/40 px-1.5 py-0.5 rounded border border-emerald-800/40">
                  <span>527 Trilha Passada / Futura:</span>
                  <span className="font-bold font-mono">
                    {interTrackData.past527.distanceKm} km ({interTrackData.past527.deltaMinutes}m) / {interTrackData.future527.distanceKm} km (+{interTrackData.future527.deltaMinutes}m)
                  </span>
                </div>
                <div className="flex justify-between text-purple-300 bg-purple-950/40 px-1.5 py-0.5 rounded border border-purple-800/40">
                  <span>529 Trilha Passada / Futura:</span>
                  <span className="font-bold font-mono">
                    {interTrackData.past529.distanceKm} km ({interTrackData.past529.deltaMinutes}m) / {interTrackData.future529.distanceKm} km (+{interTrackData.future529.deltaMinutes}m)
                  </span>
                </div>
              </div>
            )}

            {/* 527 */}
            <div className="flex justify-between items-center text-emerald-400">
              <span>NORAD 527 (OPS 0180):</span>
              <span>
                {isBeforeLaunch
                  ? 'Aguardando Lançamento'
                  : sat527Point
                  ? `${sat527Point.altitudeKm.toFixed(0)} km (Estável)`
                  : 'Em órbita'}
              </span>
            </div>

            {/* 529 */}
            <div className="flex justify-between items-center text-purple-300">
              <span>NORAD 529 (Comp. C):</span>
              <span>
                {isBeforeLaunch
                  ? 'Aguardando Lançamento'
                  : is529Decayed
                  ? 'Decaído (31/12/1963)'
                  : sat529Point
                  ? `${sat529Point.altitudeKm.toFixed(0)} km`
                  : 'Em órbita'}
              </span>
            </div>
          </div>
        </div>

        {/* Legend */}
        {!showAnchorsListDrawer && (
          <div className="absolute top-3 right-3 bg-zinc-950/85 backdrop-blur border border-zinc-800 rounded-lg p-2.5 text-[10px] font-mono text-zinc-400 space-y-1 pointer-events-none shadow z-20">
            <div className="flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 rounded-full bg-cyan-400 inline-block" />
              <span className="text-cyan-300 font-bold">528 (Alvo - Decaimento 08/11)</span>
            </div>
            {showUncertaintyBuffer && (
              <div className="flex items-center gap-1.5">
                <span className="w-2.5 h-1 border border-dashed border-cyan-400 bg-cyan-400/20 inline-block" />
                <span className="text-cyan-200">Faixa sintética (sem cobertura calibrada)</span>
              </div>
            )}
            {showObservationMarkers && (
              <div className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rotate-45 bg-amber-400 border border-white inline-block" />
                <span className="text-amber-200 font-semibold">{displayedMilestones.length} marcos simulados</span>
              </div>
            )}
            <div className="flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 inline-block" />
              <span className="text-emerald-300">527 (OPS 0180 - 485 km)</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 rounded-full bg-purple-400 inline-block" />
              <span className="text-purple-300">529 (Comp. C - Decaimento 31/12)</span>
            </div>
            <div className="flex items-center gap-1.5 pt-1 border-t border-zinc-900">
              <span className="w-2 h-2 rounded-full bg-rose-400 inline-block" />
              <span className="text-rose-300 font-semibold">Alvo Conde, BA (Anéis 100/250/500km)</span>
            </div>
          </div>
        )}
      </div>

      {/* Interactive Time Player Bar (Spans Full 1963 Timeline) */}
      <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-4 space-y-3">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          {/* Time Displays */}
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 text-zinc-200">
              <Clock className="w-4 h-4 text-cyan-400" />
              <div className="space-y-0.5">
                <div className="text-xs font-mono font-bold text-zinc-100">
                  {curDate.toISOString().replace('T', ' ').substring(0, 19)} UTC
                </div>
                <div className="text-[11px] font-mono text-zinc-400">
                  {new Date(curDate.getTime() - 3 * 3600 * 1000)
                    .toISOString()
                    .replace('T', ' ')
                    .substring(0, 19)}{' '}
                  (Horário da Bahia / UTC-3)
                </div>
              </div>
            </div>
          </div>

          {/* Player Controls & Speeds */}
          <div className="flex items-center gap-2 flex-wrap">
            <button
              onClick={() => setSimTimeMs((prev) => Math.max(LAUNCH_MS, prev - 24 * 3600 * 1000))}
              className="p-1.5 rounded bg-zinc-800 hover:bg-zinc-700 text-zinc-300 text-xs font-mono cursor-pointer"
              title="-1 Dia"
            >
              -1d
            </button>

            <button
              onClick={() => setSimTimeMs((prev) => Math.max(LAUNCH_MS, prev - 3600 * 1000))}
              className="p-1.5 rounded bg-zinc-800 hover:bg-zinc-700 text-zinc-300 text-xs font-mono cursor-pointer"
              title="-1 Hora"
            >
              -1h
            </button>

            <button
              onClick={() => setIsPlaying(!isPlaying)}
              className="px-4 py-2 rounded bg-cyan-600 hover:bg-cyan-500 text-white font-medium text-xs flex items-center gap-1.5 transition-colors cursor-pointer"
            >
              {isPlaying ? <Pause className="w-3.5 h-3.5" /> : <Play className="w-3.5 h-3.5" />}
              <span>{isPlaying ? 'Pausar' : 'Reproduzir'}</span>
            </button>

            <button
              onClick={() => setSimTimeMs((prev) => Math.min(END_OF_1963_MS, prev + 3600 * 1000))}
              className="p-1.5 rounded bg-zinc-800 hover:bg-zinc-700 text-zinc-300 text-xs font-mono cursor-pointer"
              title="+1 Hora"
            >
              +1h
            </button>

            <button
              onClick={() => setSimTimeMs((prev) => Math.min(END_OF_1963_MS, prev + 24 * 3600 * 1000))}
              className="p-1.5 rounded bg-zinc-800 hover:bg-zinc-700 text-zinc-300 text-xs font-mono cursor-pointer"
              title="+1 Dia"
            >
              +1d
            </button>

            {/* Playback Speed for Year Timeline */}
            <div className="flex items-center bg-zinc-950 rounded border border-zinc-800 ml-2">
              {[60, 3600, 86400, 604800].map((spd) => (
                <button
                  key={spd}
                  onClick={() => setPlaybackSpeed(spd)}
                  className={`px-2 py-1 text-[11px] font-mono font-medium rounded transition-colors ${
                    playbackSpeed === spd
                      ? 'bg-zinc-800 text-cyan-300 font-bold'
                      : 'text-zinc-500 hover:text-zinc-300'
                  }`}
                  title={`${spd === 60 ? '1 min/s' : spd === 3600 ? '1 hora/s' : spd === 86400 ? '1 dia/s' : '7 dias/s'}`}
                >
                  {spd === 60 ? '1m/s' : spd === 3600 ? '1h/s' : spd === 86400 ? '1d/s' : '7d/s'}
                </button>
              ))}
            </div>
          </div>
        </div>

        <p className="text-xs leading-relaxed text-zinc-300">
          {isPt ? '08/11/1963 é uma data documental, não um horário selecionável de impacto ou de radar.' : 'November 8, 1963 is a documentary date, not a selectable impact or radar timestamp.'}{' '}
          <a href="#/research/c197" className="text-cyan-300 underline underline-offset-4">{isPt ? 'Examinar o registro NASA C197–C202' : 'Read NASA record C197–C202'}</a>
        </p>
        {/* Full Year 1963 Time Slider with Milestones & Date Indicators */}
        <div className="space-y-3 pt-1">
          {/* Timeline Track with Interactive Date Pins / Indicators */}
          <div className="relative pt-6 pb-2">
            {/* Markers placed above the slider line for relevant historical dates */}
            {displayedMilestones.map((ev) => {
              const pct = Math.max(
                0,
                Math.min(100, ((ev.timestampMs - LAUNCH_MS) / (END_OF_1963_MS - LAUNCH_MS)) * 100)
              );
              const isCurrent = displayedMilestones[currentObsIndex]?.id === ev.id;
              // Visual styling per event criticality
              let pinBg = 'bg-cyan-500/80 hover:bg-cyan-400';
              let ringColor = 'border-cyan-400';
              if (ev.focalObject === 527) {
                pinBg = 'bg-emerald-500/80 hover:bg-emerald-400';
                ringColor = 'border-emerald-400';
              } else if (ev.focalObject === 529 || ev.id === 'OBS-10') {
                pinBg = 'bg-purple-500/80 hover:bg-purple-400';
                ringColor = 'border-purple-400';
              }

              return (
                <button
                  type="button"
                  key={ev.id}
                  style={{ left: `${pct}%` }}
                  className="absolute -top-1 -translate-x-1/2 flex flex-col items-center group cursor-pointer z-10 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-cyan-300"
                  aria-label={`${isPt ? 'Marco de simulação' : 'Model milestone'} ${ev.order}: ${isPt ? ev.titlePt : ev.titleEn}, ${ev.utcString.substring(0, 10)}`}
                  onClick={() => {
                    setIsPlaying(false);
                    jumpToTime(ev.timestampMs, ev);
                  }}
                  title={`#${ev.order} • ${ev.utcString.substring(0, 10)}: ${ev.titlePt}`}
                >
                  {/* Hover Tooltip */}
                  <div className="hidden group-hover:flex absolute -top-12 flex-col items-center pointer-events-none z-30 whitespace-nowrap">
                    <div className="bg-zinc-950 border border-cyan-700/80 text-cyan-200 text-[10px] font-mono px-2 py-1 rounded shadow-xl flex items-center gap-1.5">
                      <span className="font-bold text-white">#{ev.order}</span>
                      <span>{ev.utcString.substring(0, 10)}:</span>
                      <span className="text-zinc-200 font-sans max-w-[200px] truncate">{ev.titlePt}</span>
                    </div>
                    <div className="w-1.5 h-1.5 bg-cyan-700 rotate-45 -mt-0.5" />
                  </div>

                  {/* Pin Circle */}
                  <div
                    className={`w-3 h-3 rounded-full border ${ringColor} ${pinBg} transition-all duration-150 ${
                      isCurrent ? 'scale-150 ring-2 ring-white shadow-lg' : 'hover:scale-125'
                    }`}
                  />
                  {/* Stem line down to the track */}
                  <div className={`w-0.5 h-3 ${isCurrent ? 'bg-cyan-400' : 'bg-zinc-700'}`} />
                </button>
              );
            })}

            {/* Slider track */}
            <input
              type="range"
              min={LAUNCH_MS}
              max={END_OF_1963_MS}
              step={300 * 1000} // 5 min step
              value={simTimeMs}
              onChange={(e) => {
                const val = Number(e.target.value);
                setSimTimeMs(val);
                if (onTimeChange) onTimeChange(val);
              }}
              className="w-full accent-cyan-500 cursor-pointer h-2 bg-zinc-950 rounded-lg appearance-none relative z-20"
            />
          </div>

          {/* Quick Date Badges & Historical Milestones Under Timeline */}
          <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-6 gap-1.5 pt-1">
            {[
              {
                id: 'OBS-01',
                date: '16/01/1963',
                label: 'Lançamento Thor-Agena',
                color: 'text-cyan-400 border-cyan-800/80 bg-cyan-950/40',
                timeMs: new Date('1963-01-16T21:59:00Z').getTime(),
              },
              {
                id: 'OBS-03',
                date: '30/01/1963',
                label: 'Falha Bateria 527 (NRO)',
                color: 'text-emerald-400 border-emerald-800/80 bg-emerald-950/40',
                timeMs: new Date('1963-01-30T12:00:00Z').getTime(),
              },
              {
                id: 'OBS-06',
                date: '27/10/1963',
                label: 'Último TLE NORAD 528',
                color: 'text-cyan-300 border-cyan-700 bg-cyan-950/60 font-semibold',
                timeMs: new Date('1963-10-27T14:40:00Z').getTime(),
              },
            ].map((badge) => {
              const isActive = Math.abs(simTimeMs - badge.timeMs) < 12 * 3600 * 1000;
              const obs = displayedMilestones.find((o) => o.id === badge.id);
              return (
                <button
                  key={badge.id}
                  onClick={() => {
                    setIsPlaying(false);
                    jumpToTime(badge.timeMs, obs);
                  }}
                  className={`px-2 py-1.5 rounded-lg border text-left transition-all cursor-pointer ${
                    badge.color
                  } ${
                    isActive
                      ? 'ring-2 ring-white scale-102 shadow-lg brightness-110'
                      : 'hover:brightness-125 opacity-90'
                  }`}
                >
                  <div className="flex items-center justify-between text-[10px] font-mono font-bold">
                    <span>{badge.date}</span>
                    {isActive && <span className="w-1.5 h-1.5 rounded-full bg-white animate-ping" />}
                  </div>
                  <div className="text-[10px] text-zinc-300 truncate leading-tight mt-0.5">
                    {badge.label}
                  </div>
                </button>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
};
