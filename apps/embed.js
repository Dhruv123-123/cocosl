// Drop-in loader for partner sites, for every tool that isn't a calculator (calculators use money-calculators/embed.js):
//   <div class="mms-tool" data-tool="scam-checker/" data-height="760"></div>
//   <script src="https://YOUR-TOOLS-SITE/embed.js" async></script>
// Makes a responsive iframe for each div and keeps its height in sync with the tool. No cookies, no tracking.
// The page inside runs lib/embed-page.js, which hides its own header and footer and adds a small credit link.
// Make the snippet at embed.html.
(function () {
  var script = document.currentScript;
  var base = script ? script.src.replace(/embed\.js(\?.*)?$/, '') : '';
  var frames = {};
  document.querySelectorAll('.mms-tool:not([data-ready])').forEach(function (el, i) {
    // A path inside this site only: letters, digits, dashes and slashes, optionally ending in .html.
    var tool = el.getAttribute('data-tool') || '';
    if (!/^[a-z0-9-]+(\/[a-z0-9-]+)*(\/|\.html)$/.test(tool)) return;
    var id = 'mmst' + Date.now().toString(36) + i;
    var f = document.createElement('iframe');
    f.src = base + tool + '?embed=1&frame=' + id;
    f.title = (el.getAttribute('data-title') || 'Free tool').slice(0, 80);
    f.loading = 'lazy';
    var h = Math.min(Math.max(parseInt(el.getAttribute('data-height'), 10) || 800, 200), 4000);
    f.style.cssText = 'width:100%;border:0;height:' + h + 'px;display:block';
    el.setAttribute('data-ready', '1');
    el.appendChild(f);
    frames[id] = f;
  });
  window.addEventListener('message', function (e) {
    var d = e.data;
    if (!d || d.type !== 'mms-calc-height' || !frames[d.id]) return;
    if (base && e.origin !== new URL(base, location.href).origin) return;
    frames[d.id].style.height = Math.min(Math.max(d.height, 200), 4000) + 'px';
  });
})();
