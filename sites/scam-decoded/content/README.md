# Scam Decoded content files

All site copy lives here. `build.py` holds layouts and plumbing only, so the site can move to the shared builder (`docs/SITES.md`, step 3) without rewriting any words.

| Folder | Becomes | Notes |
|---|---|---|
| `pages/*.md` | `/<slug>/`, or the `path:` in front matter | `index.md` is the home page (also served at `/free/` via `alias:`); `thanks.md`, `checker.md`, `compare.md`, `privacy.md`, `disclosures.md` |
| `products/*.md` | `/kit/`, `/parents/`, `/teams/` | `layout: sales`. `product:` points at `site.json` (`product` for the kit, `ladder[]` for the others), so prices and buy links stay in one place |
| `emails/*.md` | `/emails/<slug>/email.html` + `.txt` | The 7-email welcome sequence |
| `newsletter/*.md` | `/newsletter/<slug>/` + email files | Weekly Scam Alert; see `newsletter/README.md` |

## Front matter

`title`, `description`, `path`, `layout` (`page`, the default, adds the title as an h1; `narrow`; `lead-magnet`; `sales`), `noindex: true`, `order` (sitemap and build order), `alias` + `alias_title`.
Sales pages also take `product`, `kicker`, `headline`, `lede`, `button`, `small`, `code_note`, `cover`, `cover_alt`, `cover_w`, `cover_h` and `ld_description`.

## In the body

- Markdown: `#`/`##`/`###`, lists, `**bold**`, `*italic*`, `[links](/path/)`, and pipe tables (the first column renders as row headers).
- Lines starting with `<` pass through as raw HTML.
- Blocks: `::: name` … `:::`. `cards` + `card`, `cta-band`, `disclosure` and `inside` (a styled list), plus `::: product /img/cover.png | Alt text` for the cover-and-text upsell box.
- Values: `{{site_name}}`, `{{lm_title}}`, `{{kit_name}}`, `{{kit_price}}`, `{{contact}}`, `{{reviewed}}`, `{{disclaimer}}`, `{{ai}}`… On a product page you also get `{{name}}`, `{{price}}`, `{{pages}}`, `{{refund_days}}`, `{{code}}` and `{{code_off}}`.
- Shortcodes: `{{signup:source|Button text}}`, `{{buy}}` (product page button), `{{aff:slug|Label}}` (affiliate button from `site.json` `affiliates[]`), `{{download}}`, `{{checker_box}}` and `{{checker_cta}}`.

## Moving to the shared builder later

The shared builder needs these switches (see `docs/SITES.md` on PR #4): `layout: sales` with `next:` and `code_note`; the `lead-magnet` home; placeholder hiding; and the `{{checker}}`, `{{signup}}` and `{{aff}}` shortcodes. Once it has them, copy this folder across as-is and delete `build.py` in the same PR.
