(() => {
  const cells = [...document.querySelectorAll('[data-price-cell]')];
  if (!cells.length) return;
  const endpoint = 'https://skup-zlota-gorzow.angsm111.workers.dev/api/prices';
  const maximumAge = 30 * 60 * 1000;
  const formatMoney = new Intl.NumberFormat('pl-PL', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  const formatDate = new Intl.DateTimeFormat('pl-PL', { timeZone: 'Europe/Warsaw', dateStyle: 'short', timeStyle: 'short' });
  const statusNodes = [...document.querySelectorAll('[data-price-status]')];
  let lastConfirmed = null;
  let inFlight = false;
  const fresh = stamp => Number.isFinite(stamp) && Date.now() - stamp <= maximumAge && stamp <= Date.now() + 300000;
  function clearPrices() {
    for (const cell of cells) cell.textContent = 'Potwierdź cenę';
  }
  function apply(data, snapshot = false) {
    const stamp = Date.parse(data.fetchedAt);
    if (!fresh(stamp) || data.provider === 'Dane zapasowe' || (!snapshot && data.status !== 'ok')) throw new Error('Unconfirmed price feed');
    const values = cells.map(cell => {
      const metal = data.metals?.[cell.dataset.priceCell];
      const value = snapshot ? metal?.[cell.dataset.purity] : metal?.purities?.[cell.dataset.purity]?.price;
      if (typeof value !== 'number' || !Number.isFinite(value) || value <= 0) throw new Error('Incomplete prices');
      return value;
    });
    cells.forEach((cell, index) => { cell.textContent = formatMoney.format(values[index]) + ' zł/g'; });
    lastConfirmed = stamp;
    for (const node of statusNodes) node.textContent = 'Cennik Sezam · aktualizacja: ' + formatDate.format(stamp);
  }
  async function refresh() {
    if (inFlight) return;
    inFlight = true;
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), 12000);
    try {
      const response = await fetch(endpoint, { mode: 'cors', credentials: 'omit', cache: 'no-store', signal: controller.signal });
      if (!response.ok) throw new Error('Price service unavailable');
      apply(await response.json());
    } catch {
      if (!fresh(lastConfirmed)) clearPrices();
      for (const node of statusNodes) node.textContent = fresh(lastConfirmed)
        ? 'Ostatnio potwierdzone ceny: ' + formatDate.format(lastConfirmed) + '. Ponawiamy aktualizację.'
        : 'Cennik chwilowo niedostępny. Zadzwoń: 601 775 146.';
    } finally { clearTimeout(timer); inFlight = false; }
  }
  // A static snapshot supports page rendering, but expired rates are never presented as current.
  clearPrices();
  fetch('/data/prices.json', { cache: 'no-store' }).then(r => r.ok ? r.json() : Promise.reject()).then(data => {
    if (lastConfirmed === null) apply(data, true);
  }).catch(() => {}).finally(refresh);
  setInterval(() => { if (!document.hidden) refresh(); }, 5 * 60 * 1000);
  document.addEventListener('visibilitychange', () => {
    if (!document.hidden) { if (!fresh(lastConfirmed)) clearPrices(); refresh(); }
  });
})();
