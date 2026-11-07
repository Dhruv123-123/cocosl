# Revenue model for the four brands, months 1-12 (m1 = Nov 2026). Run: python3 revenue_model.py
# Prints the markdown tables used in revenue-model-2027.md. Every input is an assumption; see that file.
MONTHS=["Nov","Dec","Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct"]
S=["C","B","O"]
def ramp(m): return (m/12)**1.5
# per brand: dict of scenario -> params; values are month-12 levels unless noted
B={
"MMS":dict(
  views={"C":3000,"B":25000,"O":150000}, watch=4.0, rpm={"C":8,"B":10,"O":13},
  subs={"C":300,"B":2500,"O":12000}, per_sub={"C":0.5,"B":1.0,"O":1.5},
  etsy={"C":10,"B":60,"O":250}, etsy_net=5.0, etsy_season={3:1.4,4:1.1},
  clicks={"C":50,"B":500,"O":3000}, conv=0.02, payout={"C":30,"B":40,"O":50}, aff_start=3, aff_season={},
  view_season={}, club=None, b2b=None),
"Scam Decoded":dict(
  views={"C":2000,"B":15000,"O":80000}, watch=3.5, rpm={"C":5,"B":6,"O":8},
  subs={"C":200,"B":1500,"O":8000}, per_sub={"C":0.4,"B":0.9,"O":1.3},
  etsy={"C":3,"B":15,"O":60}, etsy_net=5.0, etsy_season={2:1.3},
  clicks={"C":20,"B":200,"O":1500}, conv=0.015, payout={"C":20,"B":25,"O":30}, aff_start=3, aff_season={},
  view_season={}, club=None,
  b2b=dict(cu={"C":0,"B":0,"O":0}, cu_price=99, cu_paid_from=8, team={"C":0,"B":1,"O":4}, team_from=4, team_net=90)),  # credit unions moved to the B2B scenario below
"1099 Money":dict(
  views={"C":2000,"B":15000,"O":90000}, watch=5.0, rpm={"C":8,"B":10,"O":14},
  subs={"C":200,"B":1800,"O":9000}, per_sub={"C":0.8,"B":1.5,"O":2.2},
  etsy={"C":3,"B":20,"O":80}, etsy_net=8.0, etsy_season={3:1.6,4:1.5,5:1.4,6:1.4},
  clicks={"C":30,"B":300,"O":2000}, conv=0.03, payout={"C":15,"B":20,"O":25}, aff_start=3, aff_season={3:2,4:2,5:2,6:2},
  view_season={3:1.5,4:1.5,5:1.5,6:1.5}, club=dict(members={"C":0,"B":40,"O":250}, net=4.5, start=3), b2b=None),
"Dinero Simple":dict(
  views={"C":1000,"B":10000,"O":60000}, watch=4.0, rpm={"C":3,"B":4,"O":6},
  subs={"C":100,"B":800,"O":4000}, per_sub={"C":0.4,"B":0.8,"O":1.2},
  etsy={"C":2,"B":15,"O":60}, etsy_net=5.0, etsy_season={2:1.3},
  clicks={"C":0,"B":100,"O":600}, conv=0.02, payout={"C":20,"B":20,"O":20}, aff_start=6, aff_season={},
  view_season={}, club=None, b2b=None, product_start=2),
}
REF=0.3  # SparkLoop-style thank-you referrals: $ per new subscriber once list >= 500 (B and O only)
OPEN=0.40; CPM_OPENS=25; SENDS=4; SPONSOR_MIN=2500
def run(name,p,s):
    rows=[]; cum_hours=0; ypp=None; prev_subs=0
    for m in range(1,13):
        r=ramp(m)
        v=p["views"][s]*r*p["view_season"].get(m,1)
        cum_hours+=v*p["watch"]/60
        yt=0
        need=4000 if m<4 else 8000  # 4,000 hours until 31 Jan 2027, 8,000 for new applicants from 1 Feb 2027 (m4)
        if ypp is None and cum_hours>=need: ypp=m
        if ypp and m>ypp: yt=v/1000*p["rpm"][s]
        subs=p["subs"][s]*r; new=subs-prev_subs; prev_subs=subs
        prod=0 if m<p.get("product_start",1) else new*p["per_sub"][s]
        etsy=0 if m<p.get("product_start",1) else p["etsy"][s]*max(r,0.15)*p["etsy_season"].get(m,1)*p["etsy_net"]
        aff=0 if m<p["aff_start"] else p["clicks"][s]*r*p["aff_season"].get(m,1)*p["conv"]*p["payout"][s]
        ref=new*REF if (s!="C" and subs>=500) else 0
        spon=SENDS*subs*OPEN*CPM_OPENS/1000 if subs>=SPONSOR_MIN else 0
        club=0
        if p["club"] and m>=p["club"]["start"]:
            club=p["club"]["members"][s]*((m-p["club"]["start"]+1)/(13-p["club"]["start"]))*p["club"]["net"]
        b2b=0
        if p["b2b"]:
            q=p["b2b"]
            if m>=q["cu_paid_from"]: b2b+=q["cu"][s]*((m-q["cu_paid_from"]+1)/(13-q["cu_paid_from"]))*q["cu_price"]
            if m>=q["team_from"]: b2b+=q["team"][s]*q["team_net"]*min(1,(m-q["team_from"]+1)/4)
        rows.append(dict(yt=yt,prod=prod+etsy,aff=aff,email=ref+spon,club=club,b2b=b2b))
    return rows,ypp,cum_hours
out={}
for name,p in B.items():
    for s in S:
        out[(name,s)]=run(name,p,s)
def tot(r): return sum(r.values())
print("## YPP month / hours")
for k,(rows,ypp,h) in out.items(): print(k, ypp and MONTHS[ypp-1], round(h))
for s in S:
    print(f"\n### {s}: monthly net revenue by brand")
    print("| Brand | "+" | ".join(MONTHS)+" | Year 1 |"); print("|---|"+"---:|"*13)
    allm=[0]*12
    for name in B:
        rows=out[(name,s)][0]; vals=[tot(r) for r in rows]
        for i,x in enumerate(vals): allm[i]+=x
        print(f"| {name} | "+" | ".join(f"{x:,.0f}" for x in vals)+f" | **{sum(vals):,.0f}** |")
    print("| **All brands** | "+" | ".join(f"**{x:,.0f}**" for x in allm)+f" | **{sum(allm):,.0f}** |")
for s in S:
    print(f"\n### {s}: year-1 by stream")
    keys=["yt","prod","aff","email","club","b2b"]
    print("| Brand | YouTube long-form | Products | Affiliates | Email (referrals, sponsors) | Tax Club | B2B | Total | Month 12 |"); print("|---|"+"---:|"*8)
    for name in B:
        rows=out[(name,s)][0]
        sums=[sum(r[k] for r in rows) for k in keys]
        print(f"| {name} | "+" | ".join(f"{x:,.0f}" for x in sums)+f" | **{sum(sums):,.0f}** | {tot(rows[-1]):,.0f} |")

# ---------------------------------------------------------------------------
# B2B scenario (PR #13): white-label packs sold by cold email that Dhruv sends by hand.
# Funnel per email: yes-to-pilot rate -> 2 free months -> pilot-to-paid rate -> monthly churn.
B2B_PRODUCTS={
  "Weekly Scam Alert (credit unions)": dict(price=99, start=2),     # $49/$99/$149 tiers, middle tier as average
  "Money Made Simple at Work (employers)": dict(price=89, start=3), # $59/$129/$249; small employers skew to Starter
  "Scam Watch (libraries, senior centers, AAAs)": dict(price=49+150/12, start=2), # PR #13 tiers (aef8bb9): ~50% $19 single, 25% $49 2-4 sites, 15% $99 CU-sponsored, 10% $120 10-site system, + one $150 talk a year
}
B2B_SC={
  "C": dict(sends=10, yes=0.0025, convert=0.25, churn=0.04),
  "B": dict(sends=20, yes=0.01, convert=0.40, churn=0.03),
  "O": dict(sends=40, yes=0.03, convert=0.60, churn=0.02),
}
PILOT=2
def b2b_run(prod,s):
    q=B2B_SC[s]; paid=[0.0]*13; rev=[]; pilots_started=[0.0]*13
    for m in range(1,13):
        if m>=prod["start"]: pilots_started[m]=q["sends"]*q["yes"]
        new_paid=pilots_started[m-PILOT]*q["convert"] if m-PILOT>=1 else 0
        paid[m]=paid[m-1]*(1-q["churn"])+new_paid
        rev.append(paid[m]*prod["price"])
    return rev,paid[12],sum(pilots_started)
print("\n## B2B scenario")
for s in S:
    print(f"\n### B2B {s}: sends/month per product {B2B_SC[s]['sends']}, yes {B2B_SC[s]['yes']:.2%}, pilot-to-paid {B2B_SC[s]['convert']:.0%}")
    print("| Product | "+" | ".join(MONTHS)+" | Year 1 | Paying at month 12 | Pilots started |"); print("|---|"+"---:|"*15)
    allm=[0]*12
    for name,prod in B2B_PRODUCTS.items():
        rev,p12,pil=b2b_run(prod,s)
        for i,x in enumerate(rev): allm[i]+=x
        print(f"| {name} | "+" | ".join(f"{x:,.0f}" for x in rev)+f" | **{sum(rev):,.0f}** | {p12:.1f} | {pil:.1f} |")
    print("| **All B2B** | "+" | ".join(f"**{x:,.0f}**" for x in allm)+f" | **{sum(allm):,.0f}** | | |")
