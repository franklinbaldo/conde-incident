/** Only report copy success after the browser clipboard promise resolves. */
export async function copyTextToClipboard(text, clipboard) {
  if (!clipboard || typeof clipboard.writeText !== 'function') return false;
  try {
    await clipboard.writeText(text);
    return true;
  } catch {
    return false;
  }
}
