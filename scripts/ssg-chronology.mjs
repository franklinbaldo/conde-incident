// The dates are publication dates, never observation or re-entry epochs.
export function editorialChronology(stories) {
  const groups=[];
  for (const story of stories) {
    const previous=groups.at(-1);
    if (!previous || previous.date!==story.date) groups.push({date:story.date,links:[]});
    groups.at(-1).links.push('- [Capítulo '+story.chapter+': '+story.title+
      '](/conde-incident/stories/'+story.slug+'/). '+story.summary);
  }
  return groups.map(group=>'## Publicação: '+group.date+'\n\n'+group.links.join('\n')).join('\n\n');
}
