# Scam Decoded product ladder

| Step | Product | Price | Who it's for | Files |
|---|---|---|---|---|
| Free | The Scam-Proof Checklist (lead magnet) | $0 | Anyone; email sign-up | `sites/scam-decoded/static/downloads/` |
| 1 | The Family Scam-Proofing Kit | $9 | Families; the impulse buy | `family-scam-proofing-kit.html`, `LISTING.md` |
| 2 | Protect Your Parents | $29 | Adult children helping parents | `protect-your-parents/` |
| 3 | Spot It, Stop It team training pack | $99 | Small-business owners, office managers, HR | `team-training/` |

## Upsell path

- **Free checklist → kit:** email 5 (day 7) is the main kit pitch; the thanks page and `/kit/` page sell it too.
- **Kit → Protect Your Parents:** the kit's delivery message and email 7 give `KITPARENTS` ($10 off, so $19). The `/parents/` page is linked from `/kit/`.
- **Protect Your Parents → kit:** the guide's last page and delivery message offer the kit free with `GUIDEKIT`, so guide buyers get the family pieces too (and join the kit's buyer list).
- **Teams:** a different buyer. Reach it from the guide's last page, the site footer and `/teams/`, and from content aimed at work scams (fake invoices, W-2 phishing, fake IT calls). Business owners who watch the family content are the bridge.
- **Optional bundle:** Family Bundle (kit + guide) $32.

## Discount codes to create in the store before selling

| Code | Discount | Applies to | Printed in |
|---|---|---|---|
| `LAUNCH` | $4 off kit / $10 off guide | first 7 days only | kit and guide listings |
| `KITPARENTS` | $10 off | Protect Your Parents | kit delivery message, email 7, `/kit/` page |
| `GUIDEKIT` | 100% off | Family Scam-Proofing Kit | guide page 20 (via reply), guide delivery message |
| `TEAMLAUNCH` | $30 off | Spot It, Stop It | team listing, first 14 days only |

Only run launch codes while they're actually true. No fake scarcity anywhere.

## Rebuilding

```bash
cd launch/scam-decoded/product
python3 -c "from pathlib import Path; from contentfactory.business.pdf import html_to_pdf; html_to_pdf(Path('protect-your-parents/protect-your-parents.html'), Path('protect-your-parents/Protect-Your-Parents.pdf'))"
cd team-training && python3 build.py      # slides (PPTX + PDF via LibreOffice), guide, quiz, key, certificate, poster
```
