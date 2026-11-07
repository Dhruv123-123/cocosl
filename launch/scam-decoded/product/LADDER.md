# Scam Decoded product ladder

| Step | Product | Price | Who it's for | Files |
|---|---|---|---|---|
| Free | The Scam-Proof Checklist (lead magnet) | $0 | Anyone; email sign-up | `sites/scam-decoded/static/downloads/` |
| 1 | The Family Scam-Proofing Kit | $9 | Families; the impulse buy | `family-scam-proofing-kit.html`, `LISTING.md` |
| 2 | Protect Your Parents | $29 | Adult children helping parents | `protect-your-parents/` |
| 3 | Spot It, Stop It team training pack | $99 | Small-business owners, office managers, HR | `team-training/` |
| Side | Scam Decoded for Seniors (large print, Gumroad) | $7 | Older adults; gift from adult children | `seniors-pack/` |
| Side | Scam-Proof Your Parents printable kit (Gumroad) | [PRICE] | Adult child and parent, together | `parents-printable-kit/` |
| Side | Community talks (libraries, senior centers, churches) | $0–$300 | Venues; drives pack sales and email sign-ups | `speaking-kit/` |

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
cd seniors-pack && python3 build.py && cd ..   # large-print booklet, fridge checklist, wallet cards
cd speaking-kit && python3 build.py && cd ..   # talk deck (PPTX + PDF), handout, pricing sheet
cd team-training && python3 build.py      # slides (PPTX + PDF via LibreOffice), guide, quiz, key, certificate, poster
```

## Etsy

Etsy's 22 Oct 2026 rule bans AI-generated functional guides (instructions buyers rely on must be the seller's own work). Our guides say honestly that AI helped draft them, so the Seniors pack, its group license and the Scam-Proof Your Parents kit sell on Gumroad only. Only the Scam Decoded Card Set (reference cards, PR #6) stays on Etsy. The new **Scam Red Flags: Posters and Wallet Cards** (`red-flags-printables/`, $7 suggested) is signage and cards only, so it goes on Etsy and Gumroad. A guide can go back on Etsy only if Dhruv rewrites it as his own work. The catalog check is `launch/catalog/etsy_rules.py` on PR #6.
