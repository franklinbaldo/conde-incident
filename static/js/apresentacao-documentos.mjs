// PDF facsimiles rendered at 1250 px and divided into adjacent strips. See each record for the source.
const records = [
  {
    "key": "a628",
    "title": "Aerograma A-628",
    "date": "20 de novembro de 1963",
    "src": "https://media.ondisclosure.org/web/official-uap/pursue/release-05/DOS-UAP-D002_Diplomatic-Cable_Brazil_November-20-1963.pdf",
    "slot": 0
  },
  {
    "key": "fbis",
    "title": "Registro do FBIS",
    "date": "Boletim da Rádio Tupi · 8 de novembro de 1963",
    "src": "https://media.ondisclosure.org/web/official-uap/pursue/release-05/EOP-UAP-D001_NASC-Inquiry-into-Bahia-Brazil-Incident_November-13-1963.pdf",
    "slot": -1
  },
  {
    "key": "telegrama",
    "title": "Telegrama da embaixada",
    "date": "14 de novembro de 1963",
    "src": "https://media.ondisclosure.org/web/official-uap/pursue/release-05/DOS-UAP-D001_Diplomatic-Cable_Brazil_November-14-1963.pdf",
    "slot": 1
  }
];
const scans = {
  "a628": [
    {
      "width": 1250,
      "strips": [
        [
          "a628-1-1.webp",
          208
        ],
        [
          "a628-1-2.webp",
          149
        ],
        [
          "a628-1-3.webp",
          149
        ],
        [
          "a628-1-4.webp",
          107
        ],
        [
          "a628-1-5.webp",
          149
        ],
        [
          "a628-1-6.webp",
          107
        ],
        [
          "a628-1-7.webp",
          107
        ],
        [
          "a628-1-8.webp",
          77
        ],
        [
          "a628-1-9.webp",
          107
        ],
        [
          "a628-1-10.webp",
          149
        ],
        [
          "a628-1-11.webp",
          208
        ],
        [
          "a628-1-12.webp",
          101
        ]
      ]
    },
    {
      "width": 1250,
      "strips": [
        [
          "a628-2-1.webp",
          290
        ],
        [
          "a628-2-2.webp",
          290
        ],
        [
          "a628-2-3.webp",
          290
        ],
        [
          "a628-2-4.webp",
          290
        ],
        [
          "a628-2-5.webp",
          290
        ],
        [
          "a628-2-6.webp",
          168
        ]
      ]
    }
  ],
  "fbis": [
    {
      "width": 1250,
      "strips": [
        [
          "fbis-1-1.webp",
          290
        ],
        [
          "fbis-1-2.webp",
          107
        ],
        [
          "fbis-1-3.webp",
          55
        ],
        [
          "fbis-1-4.webp",
          208
        ],
        [
          "fbis-1-5.webp",
          290
        ],
        [
          "fbis-1-6.webp",
          290
        ],
        [
          "fbis-1-7.webp",
          290
        ],
        [
          "fbis-1-8.webp",
          46
        ]
      ]
    }
  ],
  "telegrama": [
    {
      "width": 1250,
      "strips": [
        [
          "telegrama-1-1.webp",
          208
        ],
        [
          "telegrama-1-2.webp",
          208
        ],
        [
          "telegrama-1-3.webp",
          149
        ],
        [
          "telegrama-1-4.webp",
          149
        ],
        [
          "telegrama-1-5.webp",
          107
        ],
        [
          "telegrama-1-6.webp",
          208
        ],
        [
          "telegrama-1-7.webp",
          107
        ],
        [
          "telegrama-1-8.webp",
          208
        ],
        [
          "telegrama-1-9.webp",
          101
        ],
        [
          "telegrama-1-10.webp",
          89
        ],
        [
          "telegrama-1-11.webp",
          84
        ]
      ]
    }
  ]
};
export const documents = records.map(record => ({
  ...record,
  pages: scans[record.key],
  pageRatio: scans[record.key][0].strips.reduce((sum, [, h]) => sum + h, 0) / scans[record.key][0].width,
}));

const assetPrefix = '/conde-incident/img/apresentacao-documentos/';
const bound = value => Math.max(0, Math.min(1, value));
const ease = t => t * t * (3 - 2 * t);

export function mountDesk(cover, view, motion, repaint) {
  const sheets = view.querySelector('[data-desk-sheets]');
  const host = cover.querySelector('[data-desk-actions]');
  const picker = host.querySelector('[data-desk-picker]');
  const readingActions = host.querySelector('[data-desk-reading-actions]');
  const back = host.querySelector('[data-desk-back]');
  const fit = host.querySelector('[data-desk-fit]');
  const pdf = host.querySelector('[data-desk-pdf]');
  const reader = cover.querySelector('[data-desk-reader]');
  const pagesNode = reader.querySelector('[data-desk-pages]');
  let depth = 0;
  let selected = documents[0];
  let tableVisible = false;
  let visiblePaper = false;
  let frame = 0;
  let timer = 0;

  const planes = documents.map(doc => {
    const plane = document.createElement('button');
    const thumbnail = document.createElement('img');
    plane.type = 'button';
    plane.tabIndex = -1;
    plane.className = 'descent-layer desk-paper';
    plane.dataset.sheet = doc.key;
    plane.setAttribute('aria-label', doc.title);
    thumbnail.src = assetPrefix + doc.key + '-capa.webp';
    thumbnail.alt = '';
    plane.append(thumbnail);
    plane.addEventListener('click', () => open(doc));
    sheets.append(plane);
    const button = document.createElement('button');
    button.type = 'button';
    button.textContent = doc.title;
    button.addEventListener('click', () => open(doc));
    picker.append(button);
    return { doc, plane };
  });

  function cancel() {
    if (frame) cancelAnimationFrame(frame);
    if (timer) clearTimeout(timer);
    frame = timer = 0;
  }

  function reveal(doc) {
    const nodes = doc.pages.map((page, index) => {
      const sheet = document.createElement('section');
      const title = document.createElement('h3');
      title.textContent = doc.title + ' · ' + doc.date + ' · folha ' + (index + 1) + ' de ' + doc.pages.length;
      sheet.append(title);
      for (const [leaf, height] of page.strips) {
        const tile = document.createElement('img');
        tile.src = assetPrefix + leaf;
        tile.width = page.width;
        tile.height = height;
        tile.alt = '';
        tile.loading = index ? 'lazy' : 'eager';
        sheet.append(tile);
      }
      return sheet;
    });
    pagesNode.replaceChildren(...nodes);
    pdf.href = doc.src;
    reader.setAttribute('aria-label', doc.title + ' · fac-símile ampliado');
    reader.hidden = false;
    reader.removeAttribute('data-fit-page');
    fit.textContent = 'Ver página inteira';
    reader.scrollTop = 0;
    reader.scrollLeft = Math.min(105, reader.scrollWidth - reader.clientWidth);
    reader.focus({ preventScroll: true });
  }

  function paint(width, height, x, y, p, documentWidth, ratio) {
    const compact = width < 680;
    const spacing = width * (compact ? .31 : .275);
    const relativeY = doc => doc.slot ? height * .07 * p : 0;
    const focusX = selected.slot * spacing * p;
    const focusY = relativeY(selected);
    const readerWidth = Math.min(width - (compact ? 20 : 92), 940);
    const viewWidth = compact ? Math.max(680, readerWidth) : readerWidth - 18;
    const largeSize = 1 + depth * (viewWidth / documentWidth - 1);
    const nearX = (width - readerWidth) / 2 + viewWidth / 2;
    const nearY = 16 + viewWidth * selected.pageRatio / 2;
    const cameraX = x + (nearX - x) * depth - focusX * largeSize * depth;
    const cameraY = y + (nearY - y) * depth - focusY * largeSize * depth;
    const pageWidth = documentWidth * ratio * largeSize;
    reader.style.setProperty('--reader-width', readerWidth + 'px');
    reader.style.setProperty('--sheet-width', viewWidth + 'px');
    for (const { doc, plane } of planes) {
      const cx = cameraX + doc.slot * spacing * p * largeSize;
      const cy = cameraY + relativeY(doc) * largeSize;
      const onTable = pageWidth > .6 && (doc.slot === 0 || p > .53);
      plane.style.visibility = onTable && !(visiblePaper && doc === selected) ? 'visible' : 'hidden';
      if (onTable) {
        const rotation = (doc.slot ? doc.slot * 8 : -4) * (doc === selected ? 1 - depth : 1);
        plane.style.transform = 'translate3d(' + cx + 'px,' + cy + 'px,0) translate(-50%,-50%) scale('
          + pageWidth / 680 + ') rotate(' + rotation + 'deg)';
      }
    }
    return { x: cameraX, y: cameraY, scale: largeSize };
  }

  function turn(to, after) {
    cancel();
    const start = depth;
    reader.hidden = true;
    visiblePaper = false;
    cover.toggleAttribute('data-desk-reading', to === 1);
    readingActions.hidden = to !== 1;
    picker.hidden = to === 1;
    const finish = () => {
      depth = to;
      visiblePaper = to === 1;
      if (visiblePaper) reveal(selected);
      repaint();
      after?.();
    };
    if (motion.matches || start === to) {
      finish();
      return;
    }
    const startTime = performance.now();
    function tick(now) {
      const t = bound((now - startTime) / 1050);
      depth = start + (to - start) * ease(t);
      if (t < 1) {
        repaint();
        frame = requestAnimationFrame(tick);
      } else {
        frame = 0;
        finish();
      }
    }
    frame = requestAnimationFrame(tick);
  }

  function open(doc) {
    selected = doc;
    turn(1);
  }

  function table(visible, autoRead = false) {
    tableVisible = visible;
    host.hidden = !visible;
    if (!visible) {
      cancel();
      depth = 0;
      visiblePaper = false;
      reader.hidden = readingActions.hidden = true;
      picker.hidden = false;
      cover.removeAttribute('data-desk-reading');
    } else if (autoRead) {
      if (motion.matches) open(documents[0]);
      else timer = setTimeout(() => open(documents[0]), 520);
    }
  }

  function lift() {
    if (!tableVisible) return { depth: 0, set() {} };
    cancel();
    const start = depth;
    reader.hidden = readingActions.hidden = host.hidden = true;
    visiblePaper = false;
    cover.removeAttribute('data-desk-reading');
    return { depth: start, set: value => { depth = value; } };
  }

  fit.addEventListener('click', () => {
    const fitted = reader.toggleAttribute('data-fit-page');
    fit.textContent = fitted ? 'Ampliar' : 'Ver página inteira';
    reader.scrollLeft = fitted ? 0 : Math.min(105, reader.scrollWidth - reader.clientWidth);
  });
  back.addEventListener('click', () => turn(0, () => picker.querySelector('button').focus()));
  return { paint, table, lift, get busy() { return !!(frame || timer); } };
}
