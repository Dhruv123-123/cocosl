---
title: Calculadora de sueldo neto
description: Calcula cuánto te llega de verdad en cada cheque, después del impuesto federal, Seguro Social y Medicare. Gratis, en español, con las tablas federales de 2026, y lo que escribes no sale de tu celular.
---
Tu presupuesto empieza con lo que te llega, no con lo que ganas. Escribe cuánto te pagan y tu estado civil, y esta calculadora te da un estimado de lo que sale de cada cheque y de lo que llega a tu cuenta.

<style>
.pc{background:var(--card);border:1px solid var(--line);border-radius:var(--radius);padding:18px;margin:24px 0}
.pc fieldset{border:0;margin:0 0 14px;padding:0}
.pc legend{font-weight:800;margin-bottom:8px}
.pc label{display:block;font-size:14px;font-weight:650;margin:0 0 4px}
.pc input,.pc select{width:100%;box-sizing:border-box;font:inherit;font-size:16px;padding:10px 12px;border:1px solid var(--line);border-radius:10px;background:#fff;color:var(--ink)}
.pc .grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px}
.pc [hidden]{display:none!important}
.pc-res{border:2px solid var(--green-d);background:var(--tint);border-radius:12px;padding:14px;margin:6px 0 0}
.pc-res h3{margin:0 0 4px;font-size:15px;color:var(--muted);font-weight:700}
.pc-res .big{font-size:34px;font-weight:850;margin:0 0 10px;font-variant-numeric:tabular-nums}
.pc-res table{width:100%;border-collapse:collapse;font-size:15px}
.pc-res th,.pc-res td{padding:5px 0;border-bottom:1px solid var(--line);text-align:right;font-variant-numeric:tabular-nums}
.pc-res th:first-child,.pc-res td:first-child{text-align:left;font-weight:600}
.pc-res tr.net td{font-weight:850;border-bottom:0}
.pc .row-actions{display:flex;flex-wrap:wrap;gap:10px;margin:8px 0 0}
.pc button{font:inherit;font-weight:750;font-size:15px;padding:10px 16px;border-radius:999px;border:2px solid var(--ink);background:transparent;color:var(--ink);cursor:pointer}
</style>
<form class="pc" id="pc" novalidate onsubmit="return false">
<fieldset>
<legend>1. Tu pago</legend>
<div class="grid">
<div><label for="pc-type">¿Cómo te pagan?</label><select id="pc-type"><option value="hour">Por hora</option><option value="year">Salario al año</option><option value="check">Bruto por cheque</option></select></div>
<div data-for="hour"><label for="pc-rate">Pago por hora ($)</label><input id="pc-rate" inputmode="decimal" placeholder="Ej. 18" autocomplete="off"></div>
<div data-for="hour"><label for="pc-hours">Horas a la semana</label><input id="pc-hours" inputmode="decimal" placeholder="40" autocomplete="off"></div>
<div data-for="year" hidden><label for="pc-salary">Salario al año ($)</label><input id="pc-salary" inputmode="decimal" placeholder="Ej. 42000" autocomplete="off"></div>
<div data-for="check" hidden><label for="pc-gross">Bruto por cheque ($)</label><input id="pc-gross" inputmode="decimal" placeholder="Ej. 1500" autocomplete="off"></div>
<div><label for="pc-freq">¿Cada cuándo te pagan?</label><select id="pc-freq"><option value="52">Cada semana</option><option value="26" selected>Cada dos semanas</option><option value="24">Dos veces al mes (quincena)</option><option value="12">Una vez al mes</option></select></div>
</div>
</fieldset>
<fieldset>
<legend>2. Tu declaración (como en tu W-4)</legend>
<div class="grid">
<div><label for="pc-status">Estado civil para impuestos</label><select id="pc-status"><option value="single">Soltero</option><option value="mfj">Casado, declaran juntos</option><option value="hoh">Jefe de familia</option><option value="mfs">Casado, declaran por separado</option></select></div>
<div><label for="pc-kids">Hijos menores de 17</label><input id="pc-kids" inputmode="numeric" placeholder="0" autocomplete="off"></div>
<div><label for="pc-deps">Otros dependientes</label><input id="pc-deps" inputmode="numeric" placeholder="0" autocomplete="off"></div>
</div>
</fieldset>
<fieldset>
<legend>3. Deducciones y tu estado (opcional)</legend>
<div class="grid">
<div><label for="pc-401k">401(k) o 403(b) tradicional por cheque ($)</label><input id="pc-401k" inputmode="decimal" placeholder="0" autocomplete="off"></div>
<div><label for="pc-health">Seguro médico o dental antes de impuestos por cheque ($)</label><input id="pc-health" inputmode="decimal" placeholder="0" autocomplete="off"></div>
<div><label for="pc-state">Impuesto de tu estado (%)</label><input id="pc-state" inputmode="decimal" placeholder="0" autocomplete="off"></div>
</div>
<p class="small">El impuesto estatal cambia mucho: algunos estados, como Texas y Florida, no cobran impuesto sobre el sueldo, y otros cobran por tramos. Si no sabes el tuyo, déjalo en 0 y recuerda que tu cheque real puede tener una línea más.</p>
</fieldset>
<div id="pc-out" aria-live="polite"></div>
<div class="row-actions"><button type="button" id="pc-example">Ver un ejemplo</button><button type="button" id="pc-clear">Borrar todo</button></div>
</form>
<script>
(function () {
  // Federal tables for wages paid in 2026. Update every year before January:
  // brackets and standard deduction: IRS Rev. Proc. 2025-32 (sections 1(j)(2) and 63(c)); child tax credit: same, section 24;
  // Social Security wage base and rates: SSA 2026 COLA fact sheet; additional Medicare tax: IRS (0.9% over $200,000 of wages).
  var TABLES = {
    year: 2026,
    brackets: {
      single: [[12400, .10], [50400, .12], [105700, .22], [201775, .24], [256225, .32], [640600, .35], [Infinity, .37]],
      mfj: [[24800, .10], [100800, .12], [211400, .22], [403550, .24], [512450, .32], [768700, .35], [Infinity, .37]],
      hoh: [[17700, .10], [67450, .12], [105700, .22], [201750, .24], [256200, .32], [640600, .35], [Infinity, .37]],
      mfs: [[12400, .10], [50400, .12], [105700, .22], [201775, .24], [256225, .32], [384350, .35], [Infinity, .37]]
    },
    standard: { single: 16100, mfj: 32200, hoh: 24150, mfs: 16100 },
    childCredit: 2200, otherDependent: 500,
    ssRate: .062, ssWageBase: 184500, medicareRate: .0145, addlMedicareRate: .009, addlMedicareOver: 200000
  };
  var $ = function (id) { return document.getElementById(id); };
  var ids = ["pc-type", "pc-rate", "pc-hours", "pc-salary", "pc-gross", "pc-freq", "pc-status", "pc-kids", "pc-deps", "pc-401k", "pc-health", "pc-state"];
  function num(v) {
    v = String(v || "").replace(/[\s$%]/g, "");
    if (!v) return NaN;
    if (v.indexOf(",") > -1 && v.indexOf(".") > -1) v = v.replace(/,/g, "");
    else if (/^\d{1,3}(,\d{3})+$/.test(v)) v = v.replace(/,/g, "");
    else v = v.replace(",", ".");
    return /^\d*\.?\d+$/.test(v) ? parseFloat(v) : NaN;
  }
  function z(x) { return isNaN(x) || x < 0 ? 0 : x; }
  function usd(x) { return "$" + x.toLocaleString("es-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 }); }
  function bracketTax(income, table) {
    var tax = 0, low = 0;
    for (var i = 0; i < table.length && income > low; i++) {
      var top = table[i][0];
      tax += (Math.min(income, top) - low) * table[i][1];
      low = top;
    }
    return tax;
  }
  function estimate(o) {
    var F = o.freq, gross = o.grossPerCheck * F, k401 = o.k401 * F, health = o.health * F;
    var fedWages = z(gross - k401 - health), ficaWages = z(gross - health);
    var taxable = z(fedWages - TABLES.standard[o.status]);
    var fed = z(bracketTax(taxable, TABLES.brackets[o.status]) - o.kids * TABLES.childCredit - o.deps * TABLES.otherDependent);
    var ss = Math.min(ficaWages, TABLES.ssWageBase) * TABLES.ssRate;
    var med = ficaWages * TABLES.medicareRate + z(ficaWages - TABLES.addlMedicareOver) * TABLES.addlMedicareRate;
    var st = fedWages * o.statePct / 100;
    var net = gross - k401 - health - fed - ss - med - st;
    return { gross: gross, fed: fed, ss: ss, med: med, st: st, k401: k401, health: health, net: net, taxable: taxable };
  }
  function read() {
    var type = $("pc-type").value, F = parseInt($("pc-freq").value, 10), g = NaN;
    if (type === "hour") { var r = num($("pc-rate").value), h = num($("pc-hours").value); if (isNaN(h)) h = 40; g = r * h * 52 / F; }
    else if (type === "year") g = num($("pc-salary").value) / F;
    else g = num($("pc-gross").value);
    return { type: type, freq: F, grossPerCheck: g, status: $("pc-status").value, kids: Math.floor(z(num($("pc-kids").value))),
      deps: Math.floor(z(num($("pc-deps").value))), k401: z(num($("pc-401k").value)), health: z(num($("pc-health").value)), statePct: Math.min(z(num($("pc-state").value)), 20) };
  }
  function save() { var s = {}; ids.forEach(function (id) { s[id] = $(id).value; }); try { history.replaceState(null, "", "#" + encodeURIComponent(JSON.stringify(s))); } catch (e) {} }
  function load(s) { ids.forEach(function (id) { if (s && s[id] !== undefined) $(id).value = s[id]; else if ($(id).tagName === "INPUT") $(id).value = ""; }); if (!s || !s["pc-type"]) { $("pc-type").value = "hour"; $("pc-freq").value = "26"; $("pc-status").value = "single"; } }
  function calc() {
    var type = $("pc-type").value;
    Array.prototype.forEach.call(document.querySelectorAll("#pc [data-for]"), function (el) { el.hidden = el.getAttribute("data-for") !== type; });
    var o = read(), out = $("pc-out");
    if (!(o.grossPerCheck > 0)) { out.innerHTML = '<p class="small">Escribe cuánto te pagan para ver tu estimado.</p>'; return; }
    save();
    var y = estimate(o), F = o.freq, per = function (x) { return usd(x / F); };
    var rows = [["Bruto", y.gross]];
    if (y.k401) rows.push(["401(k) o 403(b)", -y.k401]);
    if (y.health) rows.push(["Seguro médico o dental", -y.health]);
    rows.push(["Impuesto federal (estimado)", -y.fed], ["Seguro Social (6.2%)", -y.ss], ["Medicare (1.45%)", -y.med]);
    if (y.st) rows.push(["Impuesto de tu estado (" + o.statePct + "%)", -y.st]);
    var html = '<div class="pc-res"><h3>Te llega en cada cheque, más o menos</h3><p class="big">' + per(Math.max(y.net, 0)) + "</p><table><thead><tr><th></th><th>Por cheque</th><th>Al año</th></tr></thead><tbody>" +
      rows.map(function (r) { return "<tr><td>" + r[0] + "</td><td>" + (r[1] < 0 ? "−" : "") + per(Math.abs(r[1])) + "</td><td>" + (r[1] < 0 ? "−" : "") + usd(Math.abs(r[1])) + "</td></tr>"; }).join("") +
      '<tr class="net"><td>Neto</td><td>' + per(Math.max(y.net, 0)) + "</td><td>" + usd(Math.max(y.net, 0)) + "</td></tr></tbody></table>" +
      '<p class="small">Estimado con las tablas federales de ' + TABLES.year + ", para un año completo en un solo trabajo. Impuestos federales como porcentaje de tu bruto: " +
      (y.gross ? ((y.fed + y.ss + y.med) / y.gross * 100).toLocaleString("es-US", { maximumFractionDigits: 1 }) : "0") + "%.</p></div>";
    out.innerHTML = html;
  }
  $("pc-example").addEventListener("click", function () {
    load({ "pc-type": "hour", "pc-rate": "18", "pc-hours": "40", "pc-freq": "26", "pc-status": "single", "pc-kids": "0", "pc-deps": "0", "pc-401k": "", "pc-health": "", "pc-state": "" });
    calc();
  });
  $("pc-clear").addEventListener("click", function () { load({}); try { history.replaceState(null, "", location.pathname); } catch (e) {} calc(); });
  ids.forEach(function (id) { $(id).addEventListener("input", calc); $(id).addEventListener("change", calc); });
  var start = null;
  try { if (location.hash.length > 1) start = JSON.parse(decodeURIComponent(location.hash.slice(1))); } catch (e) { start = null; }
  load(start || {});
  calc();
  window.__pcEstimate = estimate;
})();
</script>

## Cómo se calcula

- **Bruto al año** = tu pago por hora × tus horas × 52, o tu salario, o tu bruto por cheque × los cheques del año.
- **Impuesto federal (estimado):** al bruto le restamos tu 401(k) tradicional, tu seguro médico antes de impuestos y la deducción estándar de tu estado civil. Al resto le aplicamos los tramos federales del año. Luego restamos $2,200 por cada hijo menor de 17 y $500 por cada otro dependiente, como en el paso 3 del W-4.
- **Seguro Social:** 6.2% de tu sueldo, hasta $184,500 al año en 2026. Tu 401(k) no lo baja; tu seguro médico antes de impuestos, sí.
- **Medicare:** 1.45% de tu sueldo, más 0.9% sobre lo que pase de $200,000 al año.
- **Tu estado:** el porcentaje que escribas, sobre tu sueldo después de deducciones. Es una aproximación.

## Las tablas de 2026

| Estado civil | Deducción estándar | 10% hasta | 12% hasta | 22% hasta | 24% hasta | 32% hasta | 35% hasta |
|---|---|---|---|---|---|---|---|
| Soltero | $16,100 | $12,400 | $50,400 | $105,700 | $201,775 | $256,225 | $640,600 |
| Casado, juntos | $32,200 | $24,800 | $100,800 | $211,400 | $403,550 | $512,450 | $768,700 |
| Jefe de familia | $24,150 | $17,700 | $67,450 | $105,700 | $201,750 | $256,200 | $640,600 |
| Casado, por separado | $16,100 | $12,400 | $50,400 | $105,700 | $201,775 | $256,225 | $384,350 |

Arriba del último tramo, 37%. Los tramos se aplican al ingreso después de la deducción estándar.

Fuentes: IRS, Revenue Procedure 2025-32 (tramos, deducción estándar y crédito por hijos de 2026); Administración del Seguro Social, hoja de datos del ajuste de 2026 (tope de $184,500 y tasas de 6.2% y 1.45%); IRS, impuesto adicional de Medicare (0.9% sobre $200,000).

## Lo que esta calculadora no hace

- **No es lo que tu patrón te retiene al centavo.** Tu patrón usa las tablas de retención del IRS (Publicación 15-T) y lo que pusiste en tu W-4, y el resultado puede cambiar unos dólares por cheque.
- **No sabe si tienes dos trabajos.** Con dos trabajos, cada patrón te retiene como si fuera el único; para eso está el paso 2 del W-4 y el calculador de retenciones del IRS.
- No incluye propinas, horas extra, bonos, impuestos locales, ni las deducciones nuevas de propinas y horas extra.
- No reduce el crédito por hijos para ingresos altos ni incluye otros créditos.

## Tu privacidad

Todo se calcula en tu celular o tu computadora. Lo que escribes no se manda a ningún servidor. Para que puedas guardar o compartir tu cálculo, los números quedan en la dirección de la página (lo que va después del #).

Es información general, no asesoría fiscal.
