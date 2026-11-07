/* "Could you spot it?" quiz. Runs on your device: no network calls, nothing stored.
   Data comes from content/quiz.json via window.SD_QUIZ (see build.py quiz_tool). */
(function () {
  "use strict";

  function tierFor(score, tiers) {
    var best = tiers[tiers.length - 1];
    for (var i = 0; i < tiers.length; i++) if (score >= tiers[i].min) { best = tiers[i]; break; }
    return best;
  }

  function scoreUrl(base, score) {
    return base.replace(/\/$/, "") + "/quiz/score/" + score + "/";
  }

  if (typeof module !== "undefined" && module.exports) {
    module.exports = { tierFor: tierFor, scoreUrl: scoreUrl };
    return;
  }

  var Q = window.SD_QUIZ;
  var root = document.getElementById("sd-quiz");
  if (!Q || !root) return;
  var total = Q.questions.length, i = 0, score = 0, picked = false;

  function el(tag, cls, text) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text != null) e.textContent = text;
    return e;
  }

  function track(name, props) {
    if (typeof window.plausible === "function") window.plausible(name, { props: props || {} });
  }

  function showQuestion() {
    picked = false;
    var q = Q.questions[i];
    root.innerHTML = "";
    root.appendChild(el("p", "quiz-progress", "Question " + (i + 1) + " of " + total + " · Score " + score));
    var bar = el("div", "quiz-bar"); var fill = el("span"); fill.style.width = (i / total * 100) + "%";
    bar.appendChild(fill); root.appendChild(bar);
    var card = el("div", "quiz-message");
    card.appendChild(el("p", "quiz-meta", q.channel + " · from " + q.sender));
    card.appendChild(el("p", "quiz-text", q.message));
    root.appendChild(card);
    root.appendChild(el("p", "quiz-ask", "Scam or legit?"));
    var row = el("div", "quiz-row");
    [["scam", "Scam"], ["legit", "Legit"]].forEach(function (b) {
      var btn = el("button", "quiz-pick quiz-" + b[0], b[1]);
      btn.type = "button";
      btn.addEventListener("click", function () { answer(b[0]); });
      row.appendChild(btn);
    });
    root.appendChild(row);
    var fb = el("div", "quiz-feedback"); fb.id = "sd-quiz-feedback"; fb.setAttribute("aria-live", "polite");
    root.appendChild(fb);
    if (i > 0) root.querySelector(".quiz-pick").focus();
  }

  function answer(choice) {
    if (picked) return;
    picked = true;
    var q = Q.questions[i], right = choice === q.answer;
    if (right) score++;
    root.querySelectorAll(".quiz-pick").forEach(function (b) {
      b.disabled = true;
      if (b.classList.contains("quiz-" + q.answer)) b.classList.add("is-answer");
    });
    var fb = document.getElementById("sd-quiz-feedback");
    fb.className = "quiz-feedback " + (right ? "is-right" : "is-wrong");
    fb.appendChild(el("p", "quiz-verdict", (right ? "Right: " : "Not quite: ") + (q.answer === "scam" ? "it's a scam." : "it's legit.")));
    fb.appendChild(el("p", "quiz-tell", "The tell: " + q.tell));
    fb.appendChild(el("p", null, q.why));
    var next = el("button", "quiz-next", i + 1 < total ? "Next question" : "See my score");
    next.type = "button";
    next.addEventListener("click", function () { i++; if (i < total) showQuestion(); else showResult(); });
    fb.appendChild(next);
    next.focus();
  }

  function drawCard(tier) {
    var c = document.createElement("canvas"); c.width = 1080; c.height = 1080;
    var x = c.getContext("2d"), font = "system-ui,-apple-system,'Segoe UI',Roboto,Arial,sans-serif";
    x.fillStyle = "#0d1b2a"; x.fillRect(0, 0, 1080, 1080);
    x.fillStyle = "#2ec4b6";
    x.beginPath(); x.moveTo(540, 90); x.lineTo(600, 112); x.lineTo(600, 156); x.lineTo(540, 200); x.lineTo(480, 156); x.lineTo(480, 112); x.closePath(); x.fill();
    x.textAlign = "center";
    x.fillStyle = "#f4f1ea"; x.font = "800 52px " + font; x.fillText("COULD YOU SPOT IT?", 540, 300);
    x.fillStyle = "#ff9f1c"; x.font = "800 260px " + font; x.fillText(score + "/" + total, 540, 590);
    x.fillStyle = "#f4f1ea"; x.font = "800 72px " + font; x.fillText(tier.name, 540, 710);
    x.fillStyle = "#c9d3dc"; x.font = "500 40px " + font; x.fillText("I got " + score + " of " + total + " right. Can you beat me?", 540, 800);
    x.fillStyle = "#2ec4b6"; x.font = "700 40px " + font; x.fillText(Q.site.replace(/^https?:\/\//, "") + "/quiz/", 540, 960);
    return c;
  }

  function showResult() {
    var tier = tierFor(score, Q.tiers), link = scoreUrl(Q.site, score);
    var text = "I got " + score + "/" + total + " on the Could you spot it? scam quiz (" + tier.name + "). Can you beat me?";
    track("Quiz finished", { score: String(score) });
    root.innerHTML = "";
    root.appendChild(el("p", "kicker", "Your score"));
    root.appendChild(el("h2", "quiz-score", score + "/" + total + ": " + tier.name));
    root.appendChild(el("p", "lede", tier.line));
    var canvas = drawCard(tier); canvas.className = "quiz-card"; canvas.setAttribute("role", "img");
    canvas.setAttribute("aria-label", "Result card: " + score + " out of " + total + ", " + tier.name);
    root.appendChild(canvas);
    var row = el("div", "quiz-row");
    var dl = el("button", "quiz-share", "Download card"); dl.type = "button";
    dl.addEventListener("click", function () {
      var a = document.createElement("a"); a.download = "could-you-spot-it-" + score + ".png";
      a.href = canvas.toDataURL("image/png"); a.click(); track("Quiz card downloaded");
    });
    row.appendChild(dl);
    if (navigator.share) {
      var sh = el("button", "quiz-share", "Share"); sh.type = "button";
      sh.addEventListener("click", function () {
        canvas.toBlob(function (blob) {
          var data = { title: "Could you spot it?", text: text, url: link };
          var file = blob && typeof File === "function" ? new File([blob], "could-you-spot-it.png", { type: "image/png" }) : null;
          if (file && navigator.canShare && navigator.canShare({ files: [file] })) data.files = [file];
          navigator.share(data).then(function () { track("Quiz shared"); }).catch(function () {});
        });
      });
      row.appendChild(sh);
    }
    var cp = el("button", "quiz-share ghost", "Copy link"); cp.type = "button";
    cp.addEventListener("click", function () {
      var done = function () { cp.textContent = "Link copied"; track("Quiz link copied"); };
      if (navigator.clipboard) navigator.clipboard.writeText(text + " " + link).then(done, function () { window.prompt("Copy this:", link); });
      else window.prompt("Copy this:", link);
    });
    row.appendChild(cp);
    root.appendChild(row);
    var again = el("button", "quiz-next ghost", "Take it again"); again.type = "button";
    again.addEventListener("click", function () { i = 0; score = 0; showQuestion(); root.scrollIntoView(); });
    root.appendChild(again);
    var after = document.getElementById("sd-quiz-after"); if (after) after.hidden = false;
    root.querySelector(".quiz-score").setAttribute("tabindex", "-1");
    root.querySelector(".quiz-score").focus();
  }

  var start = document.getElementById("sd-quiz-start");
  if (start) start.addEventListener("click", function () { track("Quiz started"); showQuestion(); });
})();
