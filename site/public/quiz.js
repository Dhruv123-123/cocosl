// Money personality quiz: 6 questions, 4 personalities, result -> 7-Day Money Reset signup.
(function () {
  var data = window.MMS_QUIZ, form = document.getElementById("quiz");
  if (!data || !form) return;
  var qs = form.querySelectorAll(".q"), bar = document.querySelector(".progress span");
  var result = document.getElementById("result"), answers = [];
  var order = ["avoider", "spender", "juggler", "saver"];

  function show(i) {
    qs.forEach(function (q, j) { q.hidden = j !== i; });
    bar.style.width = (i / qs.length * 100) + "%";
    var first = qs[i] && qs[i].querySelector(".opt");
    if (first && i > 0) first.focus();
  }

  function finish() {
    var score = {};
    answers.forEach(function (a) { score[a] = (score[a] || 0) + 1; });
    // Highest score wins; ties go to the later question's answer (the stated goal), then list order.
    var best = order.slice().sort(function (a, b) {
      return (score[b] || 0) - (score[a] || 0) || (answers.lastIndexOf(b) - answers.lastIndexOf(a));
    })[0];
    var r = data[best];
    form.hidden = true; bar.style.width = "100%";
    document.getElementById("r-name").textContent = r.emoji + " " + r.name;
    document.getElementById("r-summary").textContent = r.summary;
    var ol = document.getElementById("r-moves"); ol.innerHTML = "";
    r.moves.forEach(function (m) {
      var li = document.createElement("li"), a = document.createElement("a");
      a.href = m[1]; a.textContent = m[0]; li.appendChild(a); ol.appendChild(li);
    });
    result.querySelectorAll('input[name="source"],input[name="tag"],input[name="fields[source]"]').forEach(function (s) {
      s.value = "quiz-" + best;
    });
    result.hidden = false;
    document.getElementById("r-name").scrollIntoView({ behavior: "smooth", block: "start" });
    if (window.plausible) window.plausible("Quiz Complete", { props: { result: best } });
    try { localStorage.setItem("mms_quiz", best); } catch (e) {}
  }

  form.addEventListener("click", function (ev) {
    var b = ev.target.closest(".opt"); if (!b) return;
    answers.push(b.getAttribute("data-v"));
    if (answers.length < qs.length) show(answers.length); else finish();
  });
  document.getElementById("retake").addEventListener("click", function () {
    answers = []; result.hidden = true; form.hidden = false; show(0);
  });
  show(0);
})();
