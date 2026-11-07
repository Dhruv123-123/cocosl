---
title: Calculadora de envíos de dinero
description: Compara cuánto te cuesta de verdad mandar dinero a tu familia, comisión más tipo de cambio, y cuánto llega allá. Gratis, en español, y lo que escribes no sale de tu celular.
---
La comisión es solo la mitad del costo de tu envío. La otra mitad está escondida en el tipo de cambio. Escribe cuánto mandas, el tipo de cambio del mercado y lo que te muestra cada servicio antes de pagar, y la calculadora te dice cuánto pagas de verdad, cuánto llega allá y cuánto suma en un año.

<style>
.rc{background:var(--card);border:1px solid var(--line);border-radius:var(--radius);padding:18px;margin:24px 0}
.rc fieldset{border:0;margin:0 0 14px;padding:0}
.rc legend{font-weight:800;margin-bottom:8px}
.rc label{display:block;font-size:14px;font-weight:650;margin:0 0 4px}
.rc input,.rc select{width:100%;box-sizing:border-box;font:inherit;font-size:16px;padding:10px 12px;border:1px solid var(--line);border-radius:10px;background:#fff;color:var(--ink)}
.rc .grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px}
.rc .prov{border:1px solid var(--line);border-radius:12px;padding:12px;margin:0 0 12px;background:var(--paper)}
.rc .prov .grid{grid-template-columns:repeat(auto-fit,minmax(130px,1fr))}
.rc .row-actions{display:flex;flex-wrap:wrap;gap:10px;margin:6px 0 4px}
.rc button{font:inherit;font-weight:750;font-size:15px;padding:10px 16px;border-radius:999px;border:2px solid var(--ink);background:var(--ink);color:var(--paper);cursor:pointer}
.rc button.ghost{background:transparent;color:var(--ink)}
.rc .x{float:right;border:0;background:transparent;color:var(--muted);padding:2px 6px;font-size:14px}
.rc .warn{font-size:13px;color:#8a4b00;margin:8px 0 0}
.rc-out{margin:8px 0 0}
.rc-card{border:2px solid var(--line);border-radius:12px;padding:12px 14px;margin:0 0 10px;background:#fff}
.rc-card.best{border-color:var(--green-d);background:var(--tint)}
.rc-card h3{margin:0 0 6px;font-size:18px}
.rc-card .tag{display:inline-block;font-size:12px;font-weight:800;letter-spacing:.06em;text-transform:uppercase;background:var(--green-d);color:#fff;border-radius:999px;padding:2px 8px;margin-left:6px;vertical-align:middle}
.rc-card dl{display:grid;grid-template-columns:1fr auto;gap:2px 12px;margin:0;font-size:15px}
.rc-card dt{color:var(--muted)}
.rc-card dd{margin:0;font-weight:700;text-align:right;font-variant-numeric:tabular-nums}
.rc-sum{font-size:16px;margin:12px 0 0}
</style>
<form class="rc" id="rc" novalidate onsubmit="return false">
<fieldset>
<legend>1. Tu envío</legend>
<div class="grid">
<div><label for="rc-amount">¿Cuántos dólares mandas?</label><input id="rc-amount" inputmode="decimal" placeholder="300" autocomplete="off"></div>
<div><label for="rc-cur">Moneda de allá</label><select id="rc-cur"><option value="MXN">Peso mexicano (MXN)</option><option value="GTQ">Quetzal (GTQ)</option><option value="HNL">Lempira (HNL)</option><option value="DOP">Peso dominicano (DOP)</option><option value="COP">Peso colombiano (COP)</option><option value="PEN">Sol peruano (PEN)</option><option value="NIO">Córdoba (NIO)</option><option value="USD">Dólar (El Salvador, Ecuador)</option><option value="OTRA">Otra moneda</option></select></div>
<div><label for="rc-market">Tipo de cambio del mercado</label><input id="rc-market" inputmode="decimal" placeholder="Ej. 18.00" autocomplete="off"></div>
<div><label for="rc-freq">¿Cada cuándo mandas?</label><select id="rc-freq"><option value="12">Cada mes</option><option value="26">Cada quincena</option><option value="52">Cada semana</option><option value="1">Una sola vez</option></select></div>
</div>
<p class="small">El tipo de cambio del mercado es el que ves si buscas "dólar a peso" (o tu moneda) en tu buscador, el mismo día y a la misma hora que cotizas.</p>
</fieldset>
<fieldset>
<legend>2. Lo que te muestra cada servicio antes de pagar</legend>
<div id="rc-provs"></div>
<div class="row-actions"><button type="button" class="ghost" id="rc-add">+ Agregar otro servicio</button><button type="button" class="ghost" id="rc-example">Ver un ejemplo</button><button type="button" class="ghost" id="rc-clear">Borrar todo</button></div>
<p class="small">Escribe la comisión y el tipo de cambio exactos que te muestra la app o la tienda, antes de pagar. No buscamos ni guardamos tarifas de ninguna empresa.</p>
</fieldset>
<div class="rc-out" id="rc-out" aria-live="polite"></div>
</form>
<template id="rc-prov-t"><div class="prov"><button type="button" class="x" aria-label="Quitar este servicio">Quitar</button><div class="grid"><div><label>Nombre (el que tú quieras)</label><input class="p-name" autocomplete="off"></div><div><label>Comisión (dólares)</label><input class="p-fee" inputmode="decimal" placeholder="0" autocomplete="off"></div><div><label>Tipo de cambio que te dan</label><input class="p-rate" inputmode="decimal" placeholder="Ej. 17.60" autocomplete="off"></div><div><label>¿Cómo pagas?</label><select class="p-pay"><option value="cuenta">Desde tu cuenta o con débito</option><option value="efectivo">En efectivo (+1% de impuesto)</option><option value="credito">Con tarjeta de crédito</option></select></div><div class="p-cc-wrap" hidden><label>Comisión de tu tarjeta (%)</label><input class="p-cc" inputmode="decimal" placeholder="Ej. 5" autocomplete="off"></div></div><p class="warn p-cc-warn" hidden>Muchas tarjetas cobran esto como adelanto en efectivo: una comisión (muchas veces 3% a 5%), una tasa más alta e intereses desde el primer día. Los intereses no están en esta cuenta.</p></div></template>
<script>
(function () {
  var $ = function (id) { return document.getElementById(id); };
  var provs = $("rc-provs"), tpl = $("rc-prov-t"), out = $("rc-out"), MAX = 5;
  function num(v) {
    v = String(v || "").replace(/[\s$]/g, "");
    if (!v) return NaN;
    if (v.indexOf(",") > -1 && v.indexOf(".") > -1) v = v.replace(/,/g, "");
    else if (/^\d{1,3}(,\d{3})+$/.test(v)) v = v.replace(/,/g, "");
    else v = v.replace(",", ".");
    return /^-?\d*\.?\d+$/.test(v) ? parseFloat(v) : NaN;
  }
  function usd(x) { return "$" + x.toLocaleString("es-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 }); }
  function cur(x, c) { return x.toLocaleString("es-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + " " + (c === "OTRA" ? "" : c); }
  function pct(x) { return (x * 100).toLocaleString("es-US", { maximumFractionDigits: 1 }) + "%"; }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (ch) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[ch]; }); }
  function addProv(d) {
    if (provs.children.length >= MAX) return;
    var node = tpl.content.firstElementChild.cloneNode(true), n = provs.children.length + 1;
    node.querySelector(".p-name").placeholder = "Servicio " + "ABCDE"[n - 1];
    d = d || {};
    node.querySelector(".p-name").value = d.name || "";
    node.querySelector(".p-fee").value = d.fee || "";
    node.querySelector(".p-rate").value = d.rate || "";
    node.querySelector(".p-pay").value = d.pay || "cuenta";
    node.querySelector(".p-cc").value = d.cc || "";
    node.querySelectorAll("label").forEach(function (l, i) { var f = l.nextElementSibling; f.id = "rc-p" + n + "-" + i + "-" + Date.now(); l.htmlFor = f.id; });
    node.querySelector(".x").addEventListener("click", function () { node.remove(); if (!provs.children.length) addProv(); calc(); });
    node.addEventListener("input", calc);
    node.addEventListener("change", calc);
    provs.appendChild(node);
    $("rc-add").hidden = provs.children.length >= MAX;
  }
  function state() {
    return { a: $("rc-amount").value, c: $("rc-cur").value, m: $("rc-market").value, f: $("rc-freq").value,
      p: Array.prototype.map.call(provs.children, function (n) { return { name: n.querySelector(".p-name").value, fee: n.querySelector(".p-fee").value, rate: n.querySelector(".p-rate").value, pay: n.querySelector(".p-pay").value, cc: n.querySelector(".p-cc").value }; }) };
  }
  function load(s) {
    $("rc-amount").value = s.a || ""; $("rc-cur").value = s.c || "MXN"; $("rc-market").value = s.m || ""; $("rc-freq").value = s.f || "12";
    provs.innerHTML = ""; (s.p && s.p.length ? s.p : [{}, {}, {}]).slice(0, MAX).forEach(addProv);
  }
  function save() { try { history.replaceState(null, "", "#" + encodeURIComponent(JSON.stringify(state()))); } catch (e) {} }
  function calc() {
    var s = state(), A = num(s.a), M = num(s.m), F = parseInt(s.f, 10) || 12, c = s.c, rows = [];
    Array.prototype.forEach.call(provs.children, function (n) {
      var pay = n.querySelector(".p-pay").value, isCC = pay === "credito";
      n.querySelector(".p-cc-wrap").hidden = !isCC; n.querySelector(".p-cc-warn").hidden = !isCC;
    });
    if (A > 0) save();
    if (!(A > 0)) { out.innerHTML = '<p class="small">Escribe cuántos dólares mandas para empezar.</p>'; return; }
    if (c === "USD") M = 1;
    s.p.forEach(function (p, i) {
      var R = c === "USD" ? 1 : num(p.rate), fee = num(p.fee); if (isNaN(fee)) fee = 0;
      if (!(R > 0)) return;
      var tax = p.pay === "efectivo" ? A * 0.01 : 0, ccp = num(p.cc), cc = p.pay === "credito" && ccp > 0 ? (A + fee) * ccp / 100 : 0;
      var fx = M > 0 ? A * (M - R) / M : NaN, paid = A + fee + tax + cc, got = A * R;
      var cost = (isNaN(fx) ? 0 : Math.max(fx, 0)) + fee + tax + cc;
      rows.push({ name: p.name.trim() || ("Servicio " + "ABCDE"[i]), fee: fee, tax: tax, cc: cc, fx: fx, paid: paid, got: got, cost: cost, per100: got / paid * 100, pay: p.pay, ccMissing: p.pay === "credito" && !(ccp > 0), better: M > 0 && R > M });
    });
    if (!rows.length) { out.innerHTML = '<p class="small">Escribe el tipo de cambio que te da al menos un servicio.</p>'; return; }
    var useCost = M > 0 || c === "USD", score = function (r) { return useCost ? -r.cost : r.per100; };
    var sorted = rows.slice().sort(function (x, y) { return score(y) - score(x); }), best = sorted[0], worst = sorted[sorted.length - 1];
    var html = sorted.map(function (r) {
      var lines = [["Llega allá", cur(r.got, c)], ["Pagas en total", usd(r.paid)], ["Comisión", usd(r.fee)]];
      if (!isNaN(r.fx) && c !== "USD") lines.push(["Costo escondido en el tipo de cambio", r.fx >= 0 ? usd(r.fx) : "mejor que el mercado"]);
      if (r.tax) lines.push(["Impuesto de 1% por pagar en efectivo", usd(r.tax)]);
      if (r.cc) lines.push(["Comisión de tu tarjeta", usd(r.cc)]);
      if (!isNaN(r.fx) || c === "USD") { lines.push(["Costo total del envío", usd(r.cost)]); lines.push(["Costo como % de lo que mandas", pct(r.cost / A)]); }
      lines.push(["Llega por cada $100 que pagas", cur(r.per100, c)]);
      if (F > 1 && (!isNaN(r.fx) || c === "USD")) lines.push(["Costo en un año (" + F + " envíos)", usd(r.cost * F)]);
      var notes = "";
      if (r.ccMissing) notes += '<p class="warn">Con tarjeta de crédito, tu banco puede cobrarte un adelanto en efectivo. Escribe su comisión para incluirla.</p>';
      if (r.better) notes += '<p class="warn">Este tipo de cambio es mejor que el del mercado que escribiste. Revisa los dos números.</p>';
      return '<div class="rc-card' + (r === best && rows.length > 1 ? " best" : "") + '"><h3>' + esc(r.name) + (r === best && rows.length > 1 ? '<span class="tag">El más barato</span>' : "") + "</h3><dl>" +
        lines.map(function (l) { return "<dt>" + l[0] + "</dt><dd>" + l[1] + "</dd>"; }).join("") + "</dl>" + notes + "</div>";
    }).join("");
    if (rows.length > 1 && best !== worst) {
      if (useCost) {
        var d = worst.cost - best.cost;
        html += '<p class="rc-sum"><strong>Con ' + esc(best.name) + " te cuesta " + usd(d) + " menos que con " + esc(worst.name) + " cada envío" +
          (F > 1 ? ", unos " + usd(d * F) + " en un año" : "") + ".</strong></p>";
      } else {
        html += '<p class="rc-sum"><strong>Por cada $100 que pagas, con ' + esc(best.name) + " llegan " + cur(best.per100 - worst.per100, c) + " más que con " + esc(worst.name) + ".</strong></p>";
      }
    }
    if (!(M > 0) && c !== "USD") html += '<p class="small">Escribe el tipo de cambio del mercado para ver cuánto te cuesta el tipo de cambio de cada servicio.</p>';
    out.innerHTML = html;
  }
  $("rc-add").addEventListener("click", function () { addProv(); calc(); });
  $("rc-clear").addEventListener("click", function () { load({}); calc(); });
  $("rc-example").addEventListener("click", function () {
    load({ a: "300", c: "MXN", m: "18.00", f: "12", p: [{ name: "Ejemplo A (sin comisión)", fee: "0", rate: "17.60" }, { name: "Ejemplo B", fee: "3.99", rate: "17.85" }, { name: "Ejemplo C, en efectivo", fee: "5", rate: "17.95", pay: "efectivo" }] });
    calc();
  });
  ["rc-amount", "rc-cur", "rc-market", "rc-freq"].forEach(function (id) { $(id).addEventListener("input", calc); $(id).addEventListener("change", calc); });
  var start = {};
  try { if (location.hash.length > 1) start = JSON.parse(decodeURIComponent(location.hash.slice(1))) || {}; } catch (e) { start = {}; }
  load(start);
  calc();
})();
</script>

## Cómo se calcula

- **Llega allá** = los dólares que mandas × el tipo de cambio que te da el servicio.
- **Costo escondido en el tipo de cambio** = la diferencia entre el tipo del mercado y el que te dan, pasada a dólares. Si el mercado está a 18 y te dan 17.60, pierdes 40 centavos de peso por cada dólar: en $300 son unos $6.67.
- **Pagas en total** = lo que mandas + la comisión + el impuesto de 1% si pagas en efectivo + la comisión de tu tarjeta si pagas con crédito. La calculadora supone que la comisión se cobra aparte, como hacen casi todas las apps. Si tu servicio la descuenta de lo que mandas, escribe un poco menos en "cuántos dólares mandas".
- **Costo total del envío** = comisión + costo escondido en el tipo de cambio + impuesto + comisión de tu tarjeta. La calculadora ordena los servicios del más barato al más caro con este número, y marca el más barato. Sin el tipo del mercado, ordena por **cuánto llega por cada $100 que pagas**.

Los ejemplos de la calculadora usan números inventados. Las comisiones y los tipos de cambio cambian por empresa, por país, por forma de pago y durante el día.

## Lo que esta calculadora no hace

- No busca tarifas en internet ni las guarda. Tú escribes lo que te muestra cada servicio antes de pagar.
- No sabe cuánto tarda cada envío ni cuánto le cuesta a tu familia ir a recoger el dinero. Pregúntaselo a ellos.
- No incluye los intereses si pagas con tarjeta de crédito.

## Tu privacidad

Todo se calcula en tu celular o tu computadora. Lo que escribes no se manda a ningún servidor. Para que puedas compartir tu cálculo, los números se guardan en la dirección de la página (lo que va después del #); si copias el enlace, la otra persona ve los mismos números.

Es información general, no asesoría financiera. Desde el 1 de enero de 2026, los envíos al extranjero pagados en efectivo, con giro postal o con cheque de caja tienen un impuesto federal de 1%; pagar desde tu cuenta de banco o con débito no lo paga.
