// Signup forms: post in the background, then go to the download page.
// Works with Netlify Forms, Kit, MailerLite, Buttondown and the factory server.
// If anything goes wrong, the browser falls back to a normal form submit.
// A/B test (site.json > ab_test): the head script sets window.mmsAB; add its variant to events.
function abProps(p) {
  var t = window.mmsAB;
  if (t) { p.test = t.test; p.hero = t.hero; p.magnet = t.magnet; p.variant = t.hero + t.magnet; }
  return p;
}
(function () {
  if (window.mmsAB && window.plausible && document.querySelector(".ab-hero-a,.ab-magnet-a")) {
    window.plausible("AB Exposure", { props: abProps({ page: location.pathname }) });
  }
  document.querySelectorAll("form.signup-form").forEach(function (form) {
    form.addEventListener("submit", function (ev) {
      var hp = form.querySelector('input[name="website"]');
      if (hp && hp.value) { ev.preventDefault(); return; }          // bot
      if (!window.fetch || !window.URLSearchParams) return;          // old browser: native submit
      var action = form.getAttribute("action") || "";
      if (action.charAt(0) === "#") { ev.preventDefault(); alert("Signup isn't connected yet: set the email provider in site/site.json."); return; }
      ev.preventDefault();
      var src = form.querySelector('input[name="source"],input[name="tag"],input[name="fields[source]"]');
      if (window.plausible) window.plausible("Signup", { props: abProps({ form: src ? src.value : "signup", brand: "money-made-simple" }) });
      var btn = form.querySelector("button");
      if (btn) { btn.disabled = true; btn.textContent = "Sending…"; }
      var data = new URLSearchParams(new FormData(form));
      var isNetlify = form.hasAttribute("data-netlify");
      var url = isNetlify ? "/" : action;
      fetch(url, {
        method: "POST",
        mode: isNetlify ? "same-origin" : "no-cors",
        headers: { "Content-Type": "application/x-www-form-urlencoded", "Accept": "application/json" },
        body: data.toString()
      }).then(function () {
        try { localStorage.setItem("mms_subscribed", "1"); } catch (e) {}
        window.location.href = form.getAttribute("data-thanks");
      }).catch(function () { form.submit(); });
    });
  });
})();

// Wide tables scroll sideways on phones; only those need to be keyboard-focusable.
(function () {
  function fix() {
    document.querySelectorAll(".table[tabindex]").forEach(function (t) {
      if (t.scrollWidth <= t.clientWidth) t.removeAttribute("tabindex");
      else t.setAttribute("tabindex", "0");
    });
  }
  fix();
  window.addEventListener("resize", fix);
})();
