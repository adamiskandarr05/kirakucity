// Prefer the pinned CDN release. An identical bundled copy keeps play offline.
window.kirakuEngineReady = new Promise((resolve, reject) => {
  let settled = false, fallbackStarted = false;
  const load = (source, fallback) => {
    const script = document.createElement('script');
    script.src = source;
    script.onload = () => { if (!settled) { settled = true; resolve(); } };
    script.onerror = () => fallback ? reject(new Error('The town engine could not load.')) : useFallback();
    document.head.append(script);
  };
  const useFallback = () => { if (!settled && !fallbackStarted) { fallbackStarted = true; load('/static/assets/vendor/phaser-3.80.1.min.js', true); } };
  load('https://cdn.jsdelivr.net/npm/phaser@3.80.1/dist/phaser.min.js', false);
  setTimeout(useFallback, 3500);
});
// Report load failure when the player starts, without an unhandled rejection.
window.kirakuEngineReady.catch(() => {});
