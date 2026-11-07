# Dinero Simple lean launch

The smallest set that can go live: core site, one freebie, the welcome emails, 4 weeks of posts and 2 products.
Everything else is phase 2: written, kept, and switched off until it has been reviewed. The set is defined in
`lean/lean_launch.py`; the site hold, the review packets and the tests all read it from there.

**Review size:** native 14,383 words, 9.6–14.4 hours; attorney 2 pieces, 376 words, 1.2–1.3 hours. The packets are `review/dist/Lean-Revision-Espanol-Nativo.pdf` and `review/dist/Lean-Attorney-Review-Packet.pdf` (project files `content-factory/dinero-simple/review-packets/`).

## Phase 1 (lean launch)

| Piece | Where |
|---|---|
| Site core: home, `/free/`, `/links/`, blog index ("Muy pronto"), `/about/`, `/disclosures/`, `/privacy/`, `/terms/` | `sites/dinero-simple/` with `site.json` hold on |
| Freebie: Tu dinero en orden en 7 días (10-page PDF) | `sites/dinero-simple/lead-magnet/` → `/downloads/` |
| Welcome emails: days 0, 1, 3, 5, 7 + the Kit sales page | `brands/sequences/dinero-simple.yaml` (load into Sender) |
| Products: El Kit para Recortar Gastos ($5) and the Registro de Cuentas y Pagos printable ([PRICE], $5–7 suggested) | site product page + `products/dist/recorte-de-gastos/`; `imprimibles/dist/registro-de-cuentas/` (Etsy-safe: labels only) |
| Posts: 14 pieces over 4 weeks | `POSTING_PLAN_LEAN.md`, `content-lean.json` |

### The 4 weeks

| When | Format | Pieza |
|---|---|---|
| Semana 1 · lun 12:30 | short | El truco de las dos cuentas que evita sobregiros |
| Semana 1 · mié 12:30 | short | Encuentra tus suscripciones olvidadas en 10 minutos |
| Semana 1 · vie 12:30 | short | Activa estas 3 alertas del banco hoy |
| Semana 1 · sáb 20:00 | carousel | Tu cita mensual de 20 minutos con tu dinero |
| Semana 2 · lun 12:30 | short | Haz tu presupuesto por semana, no por mes |
| Semana 2 · mié 12:30 | short | Congela tu crédito gratis esta noche |
| Semana 2 · vie 12:30 | short | Esa cuenta 'sorpresa' estaba en el calendario |
| Semana 3 · lun 12:30 | short | $60 contra $150 en una tarjeta de $3,000 |
| Semana 3 · mié 12:30 | short | ¿Pagaste completo y tu puntaje bajó? |
| Semana 3 · vie 12:30 | short | ¿Tu app de ahorro de verdad está asegurada? |
| Semana 3 · sáb 20:00 | carousel | Avalancha contra bola de nieve, con números reales |
| Semana 4 · lun 12:30 | short | No canceles esa tarjeta vieja todavía |
| Semana 4 · mié 12:30 | short | El aumento que estás ignorando: el match de tu 401(k) |
| Semana 4 · vie 12:30 | short | La comisión que se come $18,000 |

## Phase 2 (held)

- **Site:** every article (`blog: *`), the site's own 10-email sequence (`emails: *`), the products
  `el-paquete-dinero-simple`, `el-presupuesto-de-20-minutos`, `empieza-a-invertir-con-100-al-mes`, `tu-fecha-sin-deudas`, and the pages `/calculadora-de-envios/`, `/calculadora-de-sueldo/`, `/como-ganamos-dinero/`, `/credito-sin-seguro-social/`, `/glosario/`.
  Links to held pages drop to plain text, so nothing on the live site points at a missing page.
- **Posting plans:** every plan below carries a PHASE 2: DO NOT POST banner.
- `POSTING_PLAN.md`
- `POSTING_PLAN_ALERTAS_INMIGRANTES_2027.md`
- `POSTING_PLAN_CREDITO_SIN_SS_2027.md`
- `POSTING_PLAN_ENVIOS_2027.md`
- `POSTING_PLAN_ESTAFAS.md`
- `POSTING_PLAN_HOLIDAY_2026.md`
- `POSTING_PLAN_MONTH_1.md`
- `POSTING_PLAN_MONTH_10.md`
- `POSTING_PLAN_MONTH_2.md`
- `POSTING_PLAN_MONTH_3.md`
- `POSTING_PLAN_MONTH_4.md`
- `POSTING_PLAN_MONTH_5.md`
- `POSTING_PLAN_MONTH_6.md`
- `POSTING_PLAN_MONTH_7.md`
- `POSTING_PLAN_MONTH_8.md`
- `POSTING_PLAN_MONTH_9.md`
- `POSTING_PLAN_NEWYEAR_2027.md`
- `POSTING_PLAN_RETO_AHORRO_2026.md`
- **Everything else in `launch/dinero-simple/`:** the free guides (taxes, credit, seniors), the workbook, the Etsy
  printables, the newsletter, WhatsApp kit, answer bank and workshops.

To move something into phase 1: get it reviewed with the full packets (`review/REVIEW_PACKETS.md`, ordered by go-live
date), then take its name out of the `site.json` hold, or add it to a live calendar and remove the banner.

## Go-live order

1. Send `Lean-Revision-Espanol-Nativo.pdf` to the native reviewer and `Lean-Attorney-Review-Packet.pdf` to the
   attorney. Make their fixes in the source files and rebuild.
2. Turn on the site with the hold as it is (`site.json` "hold" is already enabled).
3. Load the 5 welcome emails into Sender with the template language set to Spanish.
4. Publish the Kit on Gumroad and set its URL; list the Registro de Cuentas y Pagos on Etsy and Gumroad
   (set its price first).
5. Render the lean pack and post from `POSTING_PLAN_LEAN.md`, starting the Monday after the review is back.
