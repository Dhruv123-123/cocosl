// Drop-in loader for partner sites:
//   <div class="mms-calc" data-calc="debt-payoff" data-lang="en"></div>
//   <script src="https://YOUR-CALCULATORS-SITE/embed.js" async></script>
// Creates a responsive iframe for each div and keeps its height in sync. No cookies, no tracking.
(function () {
  var script = document.currentScript;
  var base = script ? script.src.replace(/embed\.js(\?.*)?$/, '') : '';
  var frames = {};
  document.querySelectorAll('.mms-calc:not([data-ready])').forEach(function (el, i) {
    var id = 'mms' + Date.now().toString(36) + i;
    var lang = el.getAttribute('data-lang') === 'es' ? 'es/' : '';
    var calc = (el.getAttribute('data-calc') || 'debt-payoff').replace(/[^a-z-]/g, '');
    var f = document.createElement('iframe');
    f.src = base + lang + calc + '/?embed=1&frame=' + id + (el.getAttribute('data-brand') === '0' ? '&brand=0' : '');
    f.title = el.getAttribute('data-title') || 'Money calculator';
    f.loading = 'lazy';
    f.style.cssText = 'width:100%;border:0;height:640px;display:block';
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
