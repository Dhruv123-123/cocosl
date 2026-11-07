// Progressive enhancement only: every form also works without this file.
(function () {
  "use strict";

  // Approve buttons stay disabled until every claim checkbox in the same form is ticked.
  // The server enforces the same rule, so this is a convenience, not the guard.
  function syncClaims(form) {
    var boxes = form.querySelectorAll("input[name=verified]");
    var all = Array.prototype.every.call(boxes, function (b) { return b.checked; });
    form.querySelectorAll("[data-needs-claims]").forEach(function (btn) {
      btn.disabled = !all;
      btn.title = all ? "" : "Tick every claim once you have fact-checked it";
    });
    var counter = form.querySelector("[data-claims-count]");
    if (counter) {
      var done = Array.prototype.filter.call(boxes, function (b) { return b.checked; }).length;
      counter.textContent = done + "/" + boxes.length + " checked";
    }
  }
  document.querySelectorAll("form[data-claims-form]").forEach(function (form) {
    syncClaims(form);
    form.addEventListener("change", function () { syncClaims(form); });
  });

  // Confirm destructive or outward-facing actions.
  document.addEventListener("submit", function (e) {
    var submitter = e.submitter || {};
    var msg = (submitter.dataset && submitter.dataset.confirm) || e.target.dataset.confirm;
    if (msg && !window.confirm(msg)) { e.preventDefault(); return; }
    // Prevent double submits on slow actions (publish, produce).
    if (submitter && submitter.tagName === "BUTTON" && !e.defaultPrevented) {
      setTimeout(function () { submitter.disabled = true; submitter.dataset.busy = "1"; }, 0);
    }
  });

  // Keep the current section visible in the horizontally scrolling phone nav.
  var active = document.querySelector(".nav a.active");
  if (active && active.parentNode.scrollWidth > active.parentNode.clientWidth) {
    active.parentNode.scrollLeft = active.offsetLeft - 16;
  }

  // Auto-refresh pages that are waiting for a background job, unless the user is typing.
  var refresh = document.body.dataset.refresh;
  if (refresh) {
    setInterval(function () {
      var a = document.activeElement;
      if (a && (a.tagName === "TEXTAREA" || a.tagName === "INPUT")) return;
      window.location.reload();
    }, parseInt(refresh, 10) * 1000);
  }
})();
