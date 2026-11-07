# Money Dashboard Pro: Google Sheets copy links (do this once, about 15 minutes)

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
