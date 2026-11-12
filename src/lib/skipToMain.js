/**
 * Move keyboard focus to the main landmark without changing the laboratory's
 * #/tab URL. A native href="#main-content" would be misread as an invalid
 * hash route and unexpectedly send visitors back to the summary.
 *
 * Keep href on the anchor for discovery/semantics; cancel only its navigation.
 */
export function skipToMain(event, doc = document) {
  const main = doc.getElementById('main-content');
  if (!main || typeof main.focus !== 'function') return false;
  event.preventDefault();
  main.focus();
  return true;
}
