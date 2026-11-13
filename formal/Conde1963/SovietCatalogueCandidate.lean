import Conde1963.Documentary

/-!
Bibliographic holdings of 1963 Soviet orbital-observation publications.
These are retrieval routes, not observed positions or TLE epochs. The
NASA catalogue association 527 = 1963 03A has no Soviet primary match yet.
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

end Conde1963
