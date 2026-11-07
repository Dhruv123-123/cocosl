"""Listing copy, Start Here PDF text, covers and the seller's Google Sheets setup guide for Money Dashboard Pro."""

SETUP = """# Money Dashboard Pro: Google Sheets copy links (do this once, about 15 minutes)

Buyers get a **Make a copy** link, so the template lands in their own Google Drive. You keep one master per language.

1. In Google Drive, open the **MMS template masters** folder (make it if it doesn't exist). Upload `Money-Dashboard-Pro.xlsx`
   (and `Tablero-de-Dinero-Pro.xlsx` for the Spanish one).
2. Open it with Google Sheets, then **File > Save as Google Sheets**. Delete the uploaded .xlsx from Drive and keep the Google Sheet.
3. Check the Google Sheet:
   - It opens on **Start**.
   - **Dashboard:** the yellow month cells have a dropdown, the numbers show (Money in $5,300 for Nov 2026), and all three charts draw.
   - **Transactions:** the Category column has a dropdown. Change one KROGER row to *Eating out & delivery*: the Dashboard and Budget vs Actual change.
   - **Budget vs Actual:** Shopping shows red (over budget in the example).
   - **Sinking Funds:** the Fund column on the right has a dropdown, and progress bars show.
   - If a chart looks off, click it, open the three-dot menu > **Edit chart** and set the chart type again; nothing else needs touching.
4. Rename it: *Money Dashboard Pro (Money Made Simple)* / *Tablero de dinero Pro (Money Made Simple)*.
5. **Share > General access > Anyone with the link > Viewer.** Never give anyone edit access to a master.
6. Copy the link and replace everything from `/edit` onwards with `/copy`:
   `https://docs.google.com/spreadsheets/d/<long id>/copy`
7. Test it in a private/incognito window: you should see *"Would you like to make a copy of ...?"*
8. Paste the links into `launch/dashboard-pro/links.json` (`sheet_dashboard_pro`, `sheet_tablero_pro`) and rebuild:
   `python launch/dashboard-pro/kit.py`. The Start Here PDF then carries the real button instead of the red placeholder.
9. Upload the new zip to Gumroad (see LISTING.md). Then set the free tool's upsell: in `apps/budget/config.js`, replace the
   `REPLACE_ME` link in `sheetTemplate.url` with the Gumroad product link, and the Pro box appears on the free Money Dashboard page.

**Updating later:** edit the master Google Sheet (or rebuild the .xlsx and repeat steps 1 to 4 into the same master). The
/copy link stays the same, so old PDFs keep working.
"""

LISTING_EN = """# Money Dashboard Pro: listing kit

**Price:** $12 · you keep about **$9.65** per Gumroad sale (10% + $0.50, plus card processing)

## Before you upload

1. Make the Google Sheets copy link (SETUP.md), paste it into `launch/dashboard-pro/links.json`, rebuild. Until then the
   Start Here PDF shows a red placeholder instead of the button: **don't upload it like that.**
2. After it's live, paste the Gumroad link into `apps/budget/config.js` (`sheetTemplate.url`) so the free Money Dashboard
   page offers it.

## Files to upload to Gumroad

| File | What it is |
|---|---|
| `Money-Dashboard-Pro.zip` | One download with everything (upload this) |
| `Start-Here.pdf` | The Make a copy link and setup steps (also inside the zip) |
| `Money-Dashboard-Pro.xlsx` | The spreadsheet, for Excel or Numbers (also inside the zip) |

Images: upload `cover.png` as the cover and `cover-square.png` as the thumbnail, then the screenshots in order.

## Gumroad

**Name:** Money Dashboard Pro: Google Sheets budget dashboard for your bank download (trends, budget vs actual, sinking funds)

**Summary:** Paste in your bank transactions and see 12 months of money in, spending and what's left, every category against its budget, and your sinking funds, with charts.

**Description:**

> Your bank already has all your numbers. This puts them on one page.
>
> **Money Dashboard Pro** takes your bank download (or the free Money Dashboard maker's file) and turns it into a dashboard
> you'll actually look at each month.
>
> **What you get**
> - **Dashboard:** pick a month and see money in, spending, saved and left over, next to your monthly average, plus your
>   biggest category and how many went over budget. Three charts: 12 months side by side, budget vs actual, and where the money went.
> - **Budget vs Actual:** every category for the month you pick, with a progress bar and red when you go over.
> - **12-month trends:** every category month by month, averages, totals and the share of your income you kept.
> - **Sinking funds:** car insurance, holidays, repairs, a trip. Set a target and a date and it tells you what to put away each month.
> - **Transactions:** paste and go. Category dropdown, filters, and the same 19 categories as the free tool. Transfers and card
>   payments are kept out of spending, so nothing is counted twice.
> - A Start tab with the 5-minute setup, and three months of example data to delete.
>
> **How it works**
> 1. Buy, then open the Start Here PDF in your download.
> 2. Click the link and press **Make a copy**. The sheet lands in your own Google Drive.
> 3. Paste your transactions, set your budgets (yellow cells). Everything else calculates.
>
> **Free first:** make a one-off dashboard from your bank file at moneymadesimple.netlify.app/budget/money-dashboard.html.
> Pro is the version you keep using: budgets, trends, sinking funds and charts, month after month.
>
> **Which sheet do I want?** Logging spending by hand with one tab per month? The 2027 Budget Sheet. Starting from your bank
> download and wanting the trends? This one.
>
> **Do I need Excel?** No. It's made for Google Sheets (free). The .xlsx also works in Excel and Numbers.
>
> **Privacy:** it's your own copy in your own Drive. Nothing connects to your bank.
>
> Educational organising tool, not financial advice. Example data is fictional. For personal use by the buyer; please don't resell or share the template.

**Tags:** budget spreadsheet, google sheets budget, money dashboard, sinking funds, budget vs actual, spending tracker, personal finance

**Settings:** Product type *Digital product*. Content: upload the files above. Turn off *Allow customers to pay what they want*.

**Etsy (optional, same files):** title *Money Dashboard Google Sheets Template, Budget vs Actual, Sinking Funds Tracker, 12 Month Spending Trends, Budget Spreadsheet*; 13 tags:
budget spreadsheet, google sheets budget, money dashboard, sinking funds, budget vs actual, spending tracker, monthly budget,
finance dashboard, expense tracker, budget template, savings tracker, financial planner, excel budget.
"""

LISTING_ES = """# Tablero de dinero Pro: kit de publicación

**Precio:** $12 · te quedan unos **$9.65** por venta en Gumroad

> **Espera la revisión de un hablante nativo** antes de publicar, como todo lo de Dinero Simple. Revisa sobre todo el
> texto de la pestaña Inicio, el PDF Empieza aquí y esta descripción.

## Antes de subirlo

1. Haz el enlace de copia de Google Sheets (SETUP.md), pégalo en `launch/dashboard-pro/links.json` (`sheet_tablero_pro`) y
   vuelve a generar. Mientras tanto el PDF muestra un aviso rojo en lugar del botón: **no lo subas así.**

## Archivos para Gumroad

| Archivo | Qué es |
|---|---|
| `Tablero-de-Dinero-Pro.zip` | Una sola descarga con todo (sube este) |
| `Empieza-Aqui.pdf` | El enlace para hacer una copia y los pasos (también dentro del zip) |
| `Tablero-de-Dinero-Pro.xlsx` | La hoja, para Excel o Numbers (también dentro del zip) |

Imágenes: `cover.png` como portada y `cover-square.png` como miniatura, luego las capturas en orden.

## Gumroad

**Nombre:** Tablero de dinero Pro: presupuesto en Google Sheets con lo que descargas de tu banco (tendencias, presupuesto vs real, fondos de ahorro)

**Resumen:** Pega tus movimientos del banco y ve 12 meses de lo que entra, lo que gastas y lo que te sobra, cada categoría contra su presupuesto y tus fondos de ahorro, con gráficas.

**Descripción:**

> Tu banco ya tiene todos tus números. Esto los pone en una sola página.
>
> **Tablero de dinero Pro** toma lo que descargas de tu banco (o el archivo del Tablero de dinero gratis) y lo convierte en un
> tablero que sí vas a revisar cada mes.
>
> **Qué incluye**
> - **Tablero:** elige un mes y ve lo que entra, lo que gastas, lo que ahorras y lo que te sobra, junto a tu promedio mensual,
>   tu categoría con más gasto y cuántas se pasaron del presupuesto. Tres gráficas.
> - **Presupuesto vs real:** cada categoría del mes que elijas, con barra de avance y en rojo cuando te pasas.
> - **Tendencias de 12 meses:** cada categoría mes por mes, promedios, totales y la parte de tu ingreso que guardas.
> - **Fondos de ahorro:** seguro del carro, fin de año, reparaciones, un viaje. Pon una meta y una fecha y te dice cuánto guardar al mes.
> - **Movimientos:** pega y listo. Lista de categorías, filtros y las mismas 19 categorías del tablero gratis. Las transferencias
>   y pagos de tarjeta no cuentan como gasto, para no contar nada dos veces.
> - Una pestaña Inicio con los pasos y tres meses de datos de ejemplo para borrar.
>
> **Cómo funciona**
> 1. Compra y abre el PDF Empieza aquí.
> 2. Haz clic en el enlace y elige **Hacer una copia**. La hoja queda en tu propio Google Drive.
> 3. Pega tus movimientos y pon tu presupuesto (celdas amarillas). Todo lo demás se calcula solo.
>
> **¿Necesito Excel?** No. Está hecha para Google Sheets (gratis). El .xlsx también funciona en Excel y Numbers.
>
> Herramienta educativa para organizarte, no es asesoría financiera. Los datos de ejemplo son ficticios. Para uso personal de quien la compra.

**Etiquetas:** presupuesto, hoja de cálculo, google sheets, finanzas personales, fondos de ahorro, control de gastos, presupuesto mensual
"""

COMMON = {
    "en": dict(
        lang="en", folder="money-dashboard-pro", zip="Money-Dashboard-Pro.zip", link_key="sheet_dashboard_pro",
        shot_titles=["Money Dashboard", "Budget vs actual", "Sinking funds"],
        cover_tag="Google Sheets + Excel", cover_title="Money Dashboard Pro",
        cover_sub="Paste your bank download. See 12 months of trends, budget vs actual and sinking funds, with charts.",
        pdf_title="Start here: Money Dashboard Pro", pdf_sub="Thanks for buying. Five minutes from here to your own dashboard.",
        pdf_h_copy="1. Get your copy (Google Sheets)",
        pdf_button="Make my copy of Money Dashboard Pro",
        pdf_todo="SELLER: the Make a copy link is missing. Add it to launch/dashboard-pro/links.json and rebuild before uploading.",
        pdf_steps=["Sign in to your Google account, then click the button above.", "Press Make a copy. It saves to your own Google Drive, named Copy of Money Dashboard Pro.",
                   "Open it and follow the Start tab: categories and budgets, paste your transactions, pick your months.",
                   "Getting transactions: make a free dashboard at moneymadesimple.netlify.app/budget/money-dashboard.html, open its Transactions tab, copy columns A to E and paste into cell A5 of Transactions here. Or paste your bank's CSV columns yourself: Date, Description, Category and Amount (money out negative)."],
        pdf_h_excel="Prefer Excel or Numbers?", pdf_excel=["Open Money-Dashboard-Pro.xlsx from the download. Everything works the same; charts update when you change the month."],
        pdf_h_tips="Every month, 10 minutes",
        pdf_tips=["Paste the new month's transactions under the old ones and fix any categories from the dropdown.",
                  "Move 'Month to look at' on the Dashboard forward.", "Check three things: left over, anything red on Budget vs Actual, and the sinking funds.",
                  "Give transfers between your own accounts and credit card payments the 'Transfers & card payments' category so card spending isn't counted twice."],
        legal="Educational organising tool, not financial advice. For personal use by the buyer; please don't resell or share the template. Questions: reply to your Gumroad receipt.",
        listing=LISTING_EN,
    ),
    "es": dict(
        lang="es", folder="tablero-de-dinero-pro", zip="Tablero-de-Dinero-Pro.zip", link_key="sheet_tablero_pro",
        shot_titles=["Tablero de dinero", "Presupuesto vs real", "Fondos de ahorro"],
        cover_tag="Google Sheets + Excel", cover_title="Tablero de dinero Pro",
        cover_sub="Pega lo que descargas de tu banco. Ve 12 meses de tendencias, presupuesto vs real y fondos de ahorro, con gráficas.",
        pdf_title="Empieza aquí: Tablero de dinero Pro", pdf_sub="Gracias por tu compra. Cinco minutos de aquí a tu propio tablero.",
        pdf_h_copy="1. Haz tu copia (Google Sheets)",
        pdf_button="Hacer mi copia del Tablero de dinero Pro",
        pdf_todo="VENDEDOR: falta el enlace para hacer una copia. Agrégalo en launch/dashboard-pro/links.json y vuelve a generar antes de subirlo.",
        pdf_steps=["Entra a tu cuenta de Google y haz clic en el botón de arriba.", "Elige Hacer una copia. Se guarda en tu propio Google Drive.",
                   "Ábrela y sigue la pestaña Inicio: categorías y presupuesto, pega tus movimientos y elige tus meses.",
                   "Para los movimientos: haz un tablero gratis en moneymadesimple.netlify.app/budget/tablero-dinero.html, abre su pestaña Movimientos, copia las columnas A a E y pégalas en la celda A5 de Movimientos. O pega tú las columnas del CSV de tu banco: Fecha, Descripción, Categoría y Monto (lo que sale, en negativo)."],
        pdf_h_excel="¿Prefieres Excel o Numbers?", pdf_excel=["Abre Tablero-de-Dinero-Pro.xlsx de la descarga. Todo funciona igual; las gráficas cambian cuando cambias el mes."],
        pdf_h_tips="Cada mes, 10 minutos",
        pdf_tips=["Pega los movimientos del mes nuevo debajo de los anteriores y corrige categorías con la lista.",
                  "Cambia «Mes que quieres ver» en el Tablero.", "Revisa tres cosas: lo que te sobra, lo que salga en rojo en Presupuesto vs real y los fondos de ahorro.",
                  "A las transferencias entre tus cuentas y los pagos de tarjeta ponles la categoría «Transferencias y pagos de tarjeta» para no contar dos veces."],
        legal="Herramienta educativa para organizarte, no es asesoría financiera. Para uso personal de quien la compra; por favor no la revendas ni la compartas. ¿Preguntas? Responde a tu recibo de Gumroad.",
        listing=LISTING_ES,
    ),
}

KIT = {**COMMON, "setup": SETUP}
