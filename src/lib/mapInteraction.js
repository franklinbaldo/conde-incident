// Pure interaction guards: keep documentary layer visibility and native page scrolling separate.
export function shouldShowScenarioConnections(connectionsEnabled, sistersVisible, primaryVisible) {
  return Boolean(connectionsEnabled && sistersVisible && primaryVisible);
}

// Touch is reserved for native page scrolling; keyboard/touch users have explicit pan buttons.
export function canPanWithPointer(pointerType) {
  return pointerType === 'mouse' || pointerType === 'pen';
}
