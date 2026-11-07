"""Business commands: `factory clients|order|ad|pitch|invoice|revenue|expense|product|links ...`."""
from __future__ import annotations

import json
from datetime import date


def _p(obj):
    print(json.dumps(obj, indent=2, default=str))


def register(sub, factory_fn) -> None:  # noqa: C901 - flat command table
    from . import affiliates, invoices, onboarding, pitch, products, revenue, ugc

    # ---- clients / CRM
    s = sub.add_parser("clients", help="UGC clients: list, add, import leads, status, follow-ups")
    s.add_argument("action", choices=["list", "add", "import", "status", "note", "followups", "packages"])
    s.add_argument("--id", type=int)
    s.add_argument("--name")
    s.add_argument("--email", default="")
    s.add_argument("--website", default="")
    s.add_argument("--niche", default="")
    s.add_argument("--file")
    s.add_argument("--status")
    s.add_argument("--text", default="")

    def clients(a):
        f = factory_fn(a)
        db = f.db
        if a.action == "packages":
            for k, p in ugc.PACKAGES.items():
                print(f"{k:9s} ${p.price_cents / 100:,.0f}  {p.description}")
            for k, ad in ugc.ADDONS.items():
                price = f"{ad.percent}%" if ad.percent else f"${ad.price_cents / 100:,.0f}"
                print(f"  + {k:22s} {price}  {ad.name}")
        elif a.action == "add":
            print(f"client #{ugc.add_client(db, a.name, email=a.email, website=a.website, niche=a.niche)}")
        elif a.action == "import":
            _p(pitch.import_leads_csv(db, a.file))
        elif a.action == "status":
            ugc.set_client_status(db, a.id, a.status, note=a.text)
            print(f"client #{a.id} -> {a.status}")
        elif a.action == "note":
            ugc.add_note(db, a.id, a.text)
        elif a.action == "followups":
            for c in ugc.due_follow_ups(db):
                print(f"#{c['id']} {c['name']} <{c['email']}> [{c['status']}]")
        else:
            for status, rows in ugc.pipeline(db).items():
                if rows:
                    print(f"\n{status.upper()} ({len(rows)})")
                    for c in rows:
                        print(f"  #{c['id']} {c['name']}  {c['email']}  {c['website']}")
    s.set_defaults(func=clients)

    # ---- orders
    s = sub.add_parser("order", help="create or advance a client order")
    s.add_argument("action", choices=["create", "status", "list", "invoice", "brief", "checklist", "check"])
    s.add_argument("--key", default="", help="checklist item key (order check)")
    s.add_argument("--undo", action="store_true", help="untick (order check)")
    s.add_argument("--client", type=int)
    s.add_argument("--id", type=int)
    s.add_argument("--package", default="starter")
    s.add_argument("--addon", action="append", default=[])
    s.add_argument("--rush", action="store_true")
    s.add_argument("--status")

    def order(a):
        db = factory_fn(a).db
        if a.action == "create":
            oid = ugc.create_order(db, a.client, a.package, addons=a.addon, rush=a.rush)
            o = ugc.get_order(db, oid)
            print(f"order #{oid}: {a.package} ${o['price_cents'] / 100:,.2f}")
            print(f"Next: `factory order brief --id {oid}` and send the client the questionnaire.")
        elif a.action == "brief":
            o = ugc.get_order(db, a.id)
            print(onboarding.questionnaire_markdown(o, ugc.get_client(db, o["client_id"]),
                                                    pitch.SenderProfile.from_env().name))
        elif a.action in ("checklist", "check"):
            if a.action == "check":
                onboarding.set_check(db, a.id, a.key, done=not a.undo)
            onboarding.setup_order(db, a.id)
            o = ugc.get_order(db, a.id)
            for item in o["brief"]["checklist"]:
                print(f"[{'x' if item['done'] else ' '}] {item['key']:16s} {item['label']}")
        elif a.action == "status":
            ugc.set_order_status(db, a.id, a.status)
            print(f"order #{a.id} -> {a.status}")
        elif a.action == "invoice":
            print(f"invoice #{invoices.invoice_from_order(db, a.id)} created")
        else:
            for o in ugc.orders(db):
                print(f"#{o['id']} client {o['client_id']} {o['package']} ${o['price_cents'] / 100:,.2f} [{o['status']}]")
    s.set_defaults(func=order)

    # ---- ad scripts
    s = sub.add_parser("ad", help="write (and optionally render) a spokesperson/demo ad for a client product")
    s.add_argument("product")
    s.add_argument("--brand-name", default="")
    s.add_argument("--audience", default="")
    s.add_argument("--benefit", action="append", default=[])
    s.add_argument("--render", action="store_true")
    s.add_argument("--order", type=int)

    def ad(a):
        f = factory_fn(a)
        script = ugc.write_ad_script(f.llm, ugc.AdBrief(product=a.product, brand_name=a.brand_name,
                                                         audience=a.audience, benefits=a.benefit))
        _p(script.model_dump())
        if a.render:
            _p(ugc.render_ad_video(f.settings, a.brand_name or a.product, script, order_id=a.order))
    s.set_defaults(func=ad)

    # ---- pitches
    s = sub.add_parser("pitch", help="draft outreach emails (never sends) and export them")
    s.add_argument("action", choices=["draft", "export", "optout", "today", "sent"])
    s.add_argument("--id", type=int)
    s.add_argument("--limit", type=int, default=25)
    s.add_argument("--out", default="")
    s.add_argument("--export", action="store_true", help="pitch today: also write .eml drafts + today.csv")

    def pitch_cmd(a):
        f = factory_fn(a)
        sender = pitch.SenderProfile.from_env()
        if a.action == "draft":
            if a.id:
                p = pitch.draft_pitch(f.llm, ugc.get_client(f.db, a.id), sender)
                pitch.save_pitch_draft(f.db, a.id, p)
                print(f"Subject: {p.subject}\n\n{p.body}")
            else:
                print(f"Drafted {len(pitch.draft_all(f.db, f.llm, sender, limit=a.limit))} pitches")
        elif a.action == "export":
            out = a.out or str(f.settings.output_dir / "outreach" / date.today().isoformat())
            _p(pitch.export_drafts(f.db, out, sender))
        elif a.action == "today":
            plan = pitch.outreach_today(f.db)
            print(f"Outreach for {plan['date']}: {plan['count']} email(s) to send (you send them; nothing is sent here)")
            for x in plan["follow_ups"]:
                late = f", {x['days_late']}d late" if x["days_late"] else ""
                print(f"  follow-up {x['step']}/2  #{x['client']['id']} {x['client']['name']} <{x['client']['email']}>{late}")
            for x in plan["first_touch"]:
                print(f"  first pitch     #{x['client']['id']} {x['client']['name']} <{x['client']['email']}>")
            if plan["to_draft"]:
                print(f"  {len(plan['to_draft'])} lead(s) need a draft first: `factory pitch draft`")
            if plan["count"]:
                print("After sending each one: `factory pitch sent --id N`")
            if a.export:
                out = a.out or str(f.settings.output_dir / "outreach" / f"today-{plan['date']}")
                _p(pitch.export_today(f.db, out, sender))
        elif a.action == "sent":
            res = pitch.mark_sent(f.db, a.id)
            if res["kind"] == "pitch":
                dues = ", ".join(st["due"] for st in res["cadence"]["steps"])
                print(f"client #{a.id}: pitch marked sent; follow-up drafts due {dues}")
            else:
                print(f"client #{a.id}: follow-up {res['step']['n']} marked sent")
        else:
            pitch.mark_opt_out(f.db, a.id)
            print(f"client #{a.id} opted out")
    s.set_defaults(func=pitch_cmd)

    # ---- proposals
    s = sub.add_parser("proposal", help="build a 3-page client proposal (HTML + PDF) with concepts and pricing")
    s.add_argument("--client", type=int, required=True)
    s.add_argument("--package", default="growth", choices=list(ugc.PACKAGES))
    s.add_argument("--addon", action="append", default=[], choices=[k for k in ugc.ADDONS if k != "rush"])
    s.add_argument("--rush", action="store_true")
    s.add_argument("--discount", type=float, default=0)
    s.add_argument("--product", action="append", default=[], help="product to feature (repeatable)")
    s.add_argument("--audience", default="")
    s.add_argument("--offer", default="")
    s.add_argument("--no-pdf", action="store_true")

    def proposal_cmd(a):
        from . import proposals
        f = factory_fn(a)
        res = proposals.build_proposal(f.db, a.client, a.package, a.addon, llm=f.llm, settings=f.settings,
                                       pdf=not a.no_pdf, rush=a.rush, discount_pct=a.discount,
                                       products=a.product or None, audience=a.audience, offer=a.offer)
        print(f"Proposal {res['number']}: total ${res['total_cents'] / 100:,.2f}, "
              f"deposit ${res['deposit_cents'] / 100:,.2f}")
        print(f"  HTML: {res['html']}")
        print(f"  PDF:  {res['pdf'] or ('(skipped)' if a.no_pdf else '(not available: needs node + playwright)')}")
    s.set_defaults(func=proposal_cmd)

    # ---- portfolio
    s = sub.add_parser("portfolio", help="render the sample-ad portfolio (fictional brands) and its gallery page")
    s.add_argument("action", choices=["build", "page"], help="build = render videos + page; page = page only")
    s.add_argument("--ads", default="", help="ads.json (default: launch/ugc-service/portfolio/ads.json)")
    s.add_argument("--out", default="", help="where videos/posters/portfolio.html go "
                                             "(default: <output>/ugc-portfolio)")
    s.add_argument("--copy-to", default="", help="also copy page + posters (no videos) here, e.g. the repo folder")

    def portfolio_cmd(a):
        from . import portfolio
        f = factory_fn(a)
        out = a.out or str(f.settings.output_dir / "ugc-portfolio")
        res = portfolio.build_portfolio(f.settings, a.ads or None, out, copy_to=a.copy_to or None,
                                        render=a.action == "build")
        _p(res)
    s.set_defaults(func=portfolio_cmd)

    # ---- invoices
    s = sub.add_parser("invoice", help="list, render, mark sent or paid")
    s.add_argument("action", choices=["list", "render", "sent", "paid", "void", "overdue"])
    s.add_argument("--id", type=int)

    def invoice(a):
        f = factory_fn(a)
        if a.action == "render":
            _p(invoices.save_invoice(f.settings, f.db, a.id))
        elif a.action == "sent":
            invoices.mark_sent(f.db, a.id)
        elif a.action == "paid":
            invoices.mark_paid(f.db, a.id)
            print(f"invoice #{a.id} paid; revenue recorded")
        elif a.action == "void":
            invoices.void_invoice(f.db, a.id)
        else:
            rows = invoices.overdue(f.db) if a.action == "overdue" else invoices.invoices(f.db)
            for i in rows:
                print(f"#{i['id']} {i['number']} ${i['total_cents'] / 100:,.2f} [{i['status']}] due {i.get('due_at') or ''}")
    s.set_defaults(func=invoice)

    # ---- revenue & expenses
    s = sub.add_parser("revenue", help="record or import revenue, show P&L and goal progress")
    s.add_argument("action", choices=["add", "import", "report", "ledger"])
    s.add_argument("--source", default="other")
    s.add_argument("--amount")
    s.add_argument("--brand", default="")
    s.add_argument("--note", default="")
    s.add_argument("--file")
    s.add_argument("--kind", default="generic", help="generic|gumroad|amazon|youtube|impact|shareasale")

    def rev(a):
        db = factory_fn(a).db
        if a.action == "add":
            revenue.add_revenue(db, a.source, a.amount, brand=a.brand, note=a.note)
        elif a.action == "import":
            _p(revenue.import_csv(db, a.file, a.kind, brand=a.brand))
        elif a.action == "ledger":
            for r in revenue.ledger(db):
                print(r)
        else:
            _p(revenue.summary(db))
    s.set_defaults(func=rev)

    s = sub.add_parser("expense", help="record a cost (llm, gpu, tts, stock, software, ads, other)")
    s.add_argument("category")
    s.add_argument("amount")
    s.add_argument("--note", default="")
    s.set_defaults(func=lambda a: revenue.add_expense(factory_fn(a).db, a.category, a.amount, note=a.note))

    # ---- digital products
    s = sub.add_parser("product", help="outline and build a digital product (HTML + PDF)")
    s.add_argument("action", choices=["build", "list", "listed"])
    s.add_argument("--brand")
    s.add_argument("--idea", default="")
    s.add_argument("--kind", default="guide")
    s.add_argument("--id", type=int)
    s.add_argument("--url", default="")

    def product(a):
        f = factory_fn(a)
        if a.action == "build":
            brand = f.brand(a.brand)
            outline = products.outline_product(f.llm, brand, a.idea, a.kind)
            _p(products.build_product(f.settings, brand, outline, db=f.db, kind=a.kind))
        elif a.action == "listed":
            products.set_product_listing(f.db, a.id, a.url)
        else:
            for p in products.products(f.db, a.brand):
                print(p)
    s.set_defaults(func=product)

    # ---- affiliate links
    s = sub.add_parser("links", help="affiliate links: sync from brand files, list with clicks")
    s.add_argument("action", choices=["sync", "list"])

    def links(a):
        f = factory_fn(a)
        if a.action == "sync":
            _p(affiliates.sync_from_brands(f.db, f.brands()))
        for row in affiliates.links(f.db):
            print(f"{row['slug']:16s} {row['clicks']:6d} clicks  {row['url']}")
    s.set_defaults(func=links)
