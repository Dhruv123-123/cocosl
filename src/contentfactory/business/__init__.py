"""The income side of the factory.

* `ugc`        - UGC ad-video service: packages, client CRM, orders, ad scripts.
* `pitch`      - outreach email drafts (never sent automatically) and lead import.
* `invoices`   - numbered invoices, HTML/PDF rendering, paid -> revenue.
* `products`   - digital products (guides, checklists...) rendered to HTML/PDF.
* `revenue`    - ledger, CSV importers and reports (P&L, RPM, goal tracking).
* `affiliates` - tracked /go/{slug} links and affiliate disclosure helper.
* `routes`     - FastAPI pages under /business plus the public /go redirect.

Modules are imported individually; nothing is imported here to keep startup light.
"""
