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

end Conde1963
