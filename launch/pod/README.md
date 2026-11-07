# Print-on-demand starter set (posters)

Ten challenge posters made from the Etsy printables' own chart pages, re-laid out as wall posters. Nothing has been
uploaded or listed: this folder only builds the files and the copy.

```
python launch/pod/build_pod.py            # all 10 → launch/pod/dist/ (git-ignored)
python launch/pod/build_pod.py --only savings-bingo-poster
```

Each poster folder has:

| File | What it's for |
|---|---|
| `<slug>-3x4.png` | 5400x7200 px. 9x12, 12x16 and 18x24 in posters (300 DPI at 18x24) |
| `<slug>-2x3.png` | 4800x7200 px. 8x12, 12x18 and 16x24 in (300 DPI), 24x36 in (200 DPI) |
| `<slug>-4x5.png` | 4800x6000 px. 8x10 and 16x20 in (300 DPI). 11x14 crops slightly |
| `preview.jpg` | A small preview for checking or sharing (not a listing mockup) |
| `LISTING.md` | Etsy title, 13 tags, description, settings and pricing notes |

`dist/contact-sheet.jpg` shows all ten.

Printify accepts PNG, JPEG and SVG files up to 100 MB, and recommends 300 DPI
([Printify help](https://help.printify.com/hc/en-us/articles/4483617936657)). These files are sRGB PNGs of 1-3 MB each.
Every product shows its own print area in Printify's Product Creator, so check the preview for every size before you
turn it on.

## Rules

- **Production partner:** set it in Etsy (Shop Manager > Settings > Production partners) before listing. Every
  description already says the poster is printed and shipped by our production partner.
- **AI disclosure:** every description says the designs were made with digital tools and AI assistance.
- **No money promises.** The totals on a chart are just what its numbers add up to.
- **Order one sample** (the 100 Envelope poster) before publishing anything, and check the line weight and that the
  paper takes a marker.
- See the print-on-demand ideas doc for platforms, fees and the launch plan.
