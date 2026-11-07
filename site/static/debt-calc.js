// Debt payoff calculator for /debt-payoff/. Same maths as payoff() in pseo.py and debtPayoff() in the calculators:
// a fixed monthly total (all minimums + extra); freed-up minimums roll into the current target debt.
(function () {
  var form = document.getElementById('debt-calc');
  if (!form) return;
  var out = document.getElementById('debt-out');
  var fmt = function (x) { return '$' + Math.round(x).toLocaleString('en-US'); };
  var yrs = function (m) {
    if (!isFinite(m)) return 'never';
    var y = Math.floor(m / 12), r = m % 12, p = [];
    if (y) p.push(y + ' year' + (y === 1 ? '' : 's'));
    if (r) p.push(r + ' month' + (r === 1 ? '' : 's'));
    return p.join(' ') || '0 months';
  };
  function payoff(debts, extra, strategy) {
    var lst = debts.map(function (d, i) { return { i: i, name: d.name, balance: d.balance, apr: d.apr, min: d.min }; });
    var budget = lst.reduce(function (s, d) { return s + d.min; }, 0) + extra;
    var order = lst.slice().sort(strategy === 'avalanche'
      ? function (a, b) { return b.apr - a.apr || a.balance - b.balance; }
      : function (a, b) { return a.balance - b.balance || b.apr - a.apr; });
    var month = 0, interest = 0, paid = {};
    while (lst.some(function (d) { return d.balance > 0.005; })) {
      month++;
      if (month > 1200) return { feasible: false, months: Infinity, interest: Infinity, budget: budget };
      lst.forEach(function (d) { if (d.balance > 0) { var i = d.balance * d.apr / 1200; d.balance += i; interest += i; } });
      var avail = budget;
      lst.forEach(function (d) {
        if (d.balance > 0) { var p = Math.min(d.min, d.balance, avail); d.balance -= p; avail -= p; }
      });
      for (var k = 0; k < order.length && avail > 0; k++) {
        var d = lst[order[k].i];
        if (d.balance > 0) { var p = Math.min(d.balance, avail); d.balance -= p; avail -= p; }
      }
      lst.forEach(function (d) { if (d.balance <= 0.005 && !(d.name in paid)) { d.balance = 0; paid[d.name] = month; } });
    }
    return { feasible: true, months: month, interest: interest, budget: budget, order: order.map(function (o) { return o.name; }), paid: paid };
  }
  function read() {
    var rows = document.querySelectorAll('#debt-rows tr'), debts = [];
    rows.forEach(function (r, n) {
      var v = function (name) { return r.querySelector('[name=' + name + ']').value.trim(); };
      var bal = parseFloat(v('balance')), apr = parseFloat(v('apr')), min = parseFloat(v('min'));
      if (bal > 0) debts.push({ name: v('name') || 'Debt ' + (n + 1), balance: bal, apr: apr >= 0 ? apr : 0, min: min > 0 ? min : 0 });
    });
    return debts;
  }
  function show() {
    var debts = read(), extra = Math.max(0, parseFloat(form.extra.value) || 0);
    if (!debts.length) { out.innerHTML = '<p>Add at least one debt with a balance.</p>'; return; }
    var a = payoff(debts, extra, 'avalanche'), s = payoff(debts, extra, 'snowball');
    if (!a.feasible) {
      out.innerHTML = '<p><strong>At ' + fmt(a.budget) + ' a month this debt never gets paid off:</strong> the payments don\'t cover the interest. Raise the extra payment or the minimums.</p>';
      return;
    }
    var diff = s.interest - a.interest;
    var esc = function (t) { return String(t).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); };
    var row = function (label, r) { return '<tr><th scope="row">' + label + '</th><td>' + yrs(r.months) + '</td><td>' + fmt(r.interest) + '</td><td>' + esc(r.order[0]) + '</td></tr>'; };
    out.innerHTML = '<p class="debt-headline">Paying <strong>' + fmt(a.budget) + ' a month</strong>, you\'d be debt-free in <strong>' + yrs(a.months) + '</strong> with the avalanche method.</p>' +
      '<div class="table" tabindex="0"><table><caption class="sr-only">Results</caption><thead><tr><th scope="col">Method</th><th scope="col">Time</th><th scope="col">Interest</th><th scope="col">Pays first</th></tr></thead><tbody>' +
      row('Avalanche', a) + row('Snowball', s) + '</tbody></table></div>' +
      '<p>' + (Math.abs(diff) < 1 ? 'Both methods cost the same here, so pick the one you\'ll stick with.'
        : diff > 0 ? 'Avalanche saves ' + fmt(diff) + ' in interest. Snowball clears its first debt in month ' + Math.min.apply(null, Object.values(s.paid)) + ' (avalanche: month ' + Math.min.apply(null, Object.values(a.paid)) + ').'
        : 'Snowball comes out ' + fmt(-diff) + ' cheaper with these debts.') + '</p>';
    if (window.plausible) window.plausible('Debt Calc', { props: { debts: String(debts.length) } });
  }
  form.addEventListener('submit', function (e) { e.preventDefault(); show(); });
  document.querySelectorAll('[data-load]').forEach(function (b) {
    b.addEventListener('click', function () {
      var ds = JSON.parse(b.getAttribute('data-load')), rows = document.querySelectorAll('#debt-rows tr');
      rows.forEach(function (r, n) {
        var d = ds[n];
        r.querySelector('[name=name]').value = d ? d.name : '';
        r.querySelector('[name=balance]').value = d ? d.balance : '';
        r.querySelector('[name=apr]').value = d ? d.apr : '';
        r.querySelector('[name=min]').value = d ? d.minPayment : '';
      });
      form.extra.value = b.getAttribute('data-extra');
      show();
      form.scrollIntoView({ behavior: 'smooth', block: 'start' });
      form.querySelector('input').focus({ preventScroll: true });
    });
  });
  show();
})();
