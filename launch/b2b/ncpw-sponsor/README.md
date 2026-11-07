# Consumer Protection Week package (credit unions)

Five daily white-label member alerts for National Consumer Protection Week, Mon Mar 1 – Fri Mar 5, 2027,
delivered Feb 15. Start with **[SPONSOR_PACKAGE.md](SPONSOR_PACKAGE.md)** (price, pitch, timeline, press note,
library talk).

- `issues.json`: the 5 alerts, sourced to the FTC and CFPB. Same topics, days and key facts as Scam Decoded's
  NCPW week; never mentions Scam Decoded.
- `product.json`, `brands/`: same tokens as `credit-union-alert` (CU_NAME, CU_PHONE, CU_NEVER_ASK, ...), so a
  weekly client's brand file works here as is.
- `sales-sheet.html`, `library-handout.html`: rendered to `out/*.pdf` by `python3 build.py ncpw-sponsor`.
- Deliver: `python3 deliver.py ncpw-sponsor --client credit-union-alert/clients/<slug>.json --month 2027-03`.
