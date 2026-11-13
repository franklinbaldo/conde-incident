import Conde1963.Documentary

/-!
Bibliographic holdings of 1963 Soviet orbital-observation publications.
These are retrieval routes, not observed positions or TLE epochs. The
NASA documentary aliases 527/528/529 identify labels but add no Soviet
primary match or observation; the 528/529 table was published in 1977.
No physical theorem, observation or orbital parameter is certified here.
-/

namespace Conde1963

structure SovietCatalogueRetrievalCandidate where
  sourceOccurrence : String
  sourceFamily : String
  nasaDocumentaryCrosswalk : String
  candidateNorad : Nat
  originalSovietDesignation : Option String
  issuePage : Option Nat
  observationEpochUtc : Option String
  sensorFrame : Option String
  covariance : Option String
  observedTrack : Option String
  status : String
  deriving Repr

def sovietCatalogue1963Candidates : List SovietCatalogueRetrievalCandidate :=
  (["C241-L29#1", "C241-L29#2"].flatMap fun source =>
    [527, 528, 529].map fun norad =>
      { sourceOccurrence := source
        sourceFamily := "SOVIET_INSTITUTIONAL_HOLDINGS"
        nasaDocumentaryCrosswalk := "C241-L28:527=1963 03A"
        candidateNorad := norad
        originalSovietDesignation := none
        issuePage := none
        observationEpochUtc := none
        sensorFrame := none
        covariance := none
        observedTrack := none
        status := "PENDING_NO_ISSUE_FACSIMILE" })

/-! C241-L32: NASA SSR 1977 retrospective institutional catalogue labels.
This list contains identities, not 1963 instrumental epochs, physical events,
or measurements; no orbital predicate is activated by these entries. -/
structure NasaRetrospectiveCatalogLabel where
  sourceRecord : String
  printedDesignator : String
  norad : Nat
  printedPage : Nat
  originalObservationEpochUtc : Option String
  originalSensor : Option String
  status : String
  deriving Repr

def nasaRetrospective1977Labels : List NasaRetrospectiveCatalogLabel :=
  [{ sourceRecord := "C241-L32", printedDesignator := "1963 003B",
     norad := 528, printedPage := 43, originalObservationEpochUtc := none,
     originalSensor := none, status := "DOCUMENTARY_IDENTITY_ONLY" },
   { sourceRecord := "C241-L32", printedDesignator := "1963 003C",
     norad := 529, printedPage := 43, originalObservationEpochUtc := none,
     originalSensor := none, status := "DOCUMENTARY_IDENTITY_ONLY" }]

/-! C241-L34: Alla Masevich's February 1963 preface mentions two
Soviet periodical series. These bibliographic search targets are neither
issue-level facsimiles nor observations of any target object. The printed
page of viewer image 006 and the instrumental epoch are unknown. -/
structure SovietContemporaryBibliographicLead where
  sourceRecord : String
  periodicalTitle : String
  viewerPage : Nat
  printedPage : Option Nat
  sourceWebpSha256 : String
  observedNorad : Option Nat
  observationEpochUtc : Option String
  originalIssueAuthenticated : Bool
  status : String
  deriving Repr

def sovietContemporaryBibliographicLeads :
    List SovietContemporaryBibliographicLead :=
  [{ sourceRecord := "C241-L34", periodicalTitle := "Искусственные спутники Земли",
     viewerPage := 6, printedPage := none,
     sourceWebpSha256 := "0d68650aa352f7404f4251abf53c3d117efd3dde377b6c5667df85516089f901",
     observedNorad := none, observationEpochUtc := none,
     originalIssueAuthenticated := false, status := "BIBLIOGRAPHIC_LEAD_ONLY" },
   { sourceRecord := "C241-L34",
     periodicalTitle := "Бюллетень станций оптических наблюдений искусственных спутников",
     viewerPage := 7, printedPage := some 6,
     sourceWebpSha256 := "fea39a91dae6ce25b977e4562c758818dc44667dc7559b7d99f9ecc6231f4bb2",
     observedNorad := none, observationEpochUtc := none,
     originalIssueAuthenticated := false, status := "BIBLIOGRAPHIC_LEAD_ONLY" }]

end Conde1963
