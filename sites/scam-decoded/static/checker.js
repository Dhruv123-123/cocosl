/* Scam Decoded "Is this a scam?" checker.
 * Rule-based, runs entirely in the browser: no network calls, no storage, nothing leaves the page.
 * The same file runs under Node for tests (module.exports at the bottom).
 */
(function (root) {
  "use strict";

  // ---------------------------------------------------------------- text rules
  // weight: 1 small sign, 2 red flag, 3 strong red flag, 4 near-certain scam pattern
  var TEXT_RULES = [
    { id: "gift-card", weight: 4, article: "gift-card-scams",
      label: "Asks for payment by gift card",
      why: "Only scammers ask you to pay with gift cards. Once you share the numbers, the money is gone.",
      any: [/\b(gift ?cards?|google play cards?|itunes cards?|apple gift|steam cards?|ebay cards?)\b/i] },
    { id: "read-code", weight: 4, article: "verification-code-scams",
      label: "Asks you to share a verification code",
      why: "A code is sent when someone tries to sign in as you. Whoever asks for it is the one signing in.",
      any: [/\b(read|send|share|tell|give|forward|text)\b[^.?!\n]{0,30}\b(code|otp|passcode)\b/i,
            /\b(sent|texted|gave) you (a|an|the|my)? ?(\w+ )?(code|otp)\b[^\n]{0,60}\b(mistake|accident|read|send|share|tell|give)/i,
            /\b(code|otp)\b[^.?!\n]{0,30}\b(by (mistake|accident)|read it|send it|share it|tell me)/i] },
    { id: "safe-account", weight: 4, article: "bank-impersonation-calls",
      label: "Tells you to move money to keep it safe",
      why: "No real bank, agency or company asks you to move your money to a 'safe' or 'secure' account.",
      any: [/\b(safe|secure|protected|new) (bank )?account\b[^.?!\n]{0,40}\b(move|transfer|send)\b/i,
            /\b(move|transfer|withdraw)\b[^.?!\n]{0,25}\b(money|funds|savings|balance)\b[^.?!\n]{0,40}\b(safe|secure|protect)/i] },
    { id: "overpay", weight: 4, article: "online-marketplace-scams",
      label: "Overpayment or 'send back the difference'",
      why: "Refunding an overpayment is a classic fake check and fake refund scam. The original payment disappears.",
      any: [/\b(overpaid|overpayment|refunded (you )?too much|extra (money|amount)|send (back )?the difference|return the (extra|excess))\b/i] },
    { id: "remote-access", weight: 4, article: "tech-support-scams",
      label: "Asks to connect to your computer",
      why: "Never let someone who contacted you install remote access. It gives them control of your computer and bank logins.",
      any: [/\b(anydesk|teamviewer|quick ?assist|ultraviewer|logmein|remote (access|desktop|session)|connect to your (computer|device|pc))\b/i] },
    { id: "pay-to-get-paid", weight: 4, article: "job-and-task-scams",
      label: "You have to pay to get paid",
      why: "A job, prize or refund that needs a deposit, top-up or fee first isn't real.",
      any: [/\b(top ?up|recharge|deposit|unlock)\b[^.?!\n]{0,40}\b(account|tasks?|earnings|commission|withdraw)/i,
            /\b(pay|cover)\b[^.?!\n]{0,20}\b(fee|taxes|tax|shipping|processing|customs)\b[^.?!\n]{0,40}\b(prize|winnings|claim|release|receive)\b/i] },
    { id: "secrecy", weight: 3, article: "family-emergency-scams",
      label: "Asks you to keep it secret",
      why: "Secrecy stops you from checking with someone who'd spot the scam.",
      any: [/\b(don'?t|do not|never) (tell|call|contact|mention|let)\b[^.?!\n]{0,25}\b(anyone|anybody|mom|dad|parents|family|bank|police|teller)\b/i,
            /\bkeep (this|it) (between us|secret|private|confidential|quiet)\b/i] },
    { id: "new-number", weight: 3, article: "family-emergency-scams",
      label: "A 'new number' from someone you know",
      why: "'I lost my phone, this is my new number' is how family emergency scams start. Call the old number.",
      any: [/\b(my new (phone )?number|this is my new|new phone,? new number|(lost|dropped|broke|broken|smashed) (my )?phone|phone (is )?(broken|died))\b/i] },
    { id: "emergency", weight: 2, article: "family-emergency-scams",
      label: "A family emergency that needs money now",
      why: "Panic plus urgent money is the pattern. Call the person back on a number you already have.",
      any: [/\b(bail|arrested|in jail|car accident|hospital|lawyer|attorney)\b/i] },
    { id: "crypto-wire", weight: 3, article: "investment-and-crypto-scams",
      label: "Asks for crypto, wire transfer or a Bitcoin ATM",
      why: "Crypto, wires and Bitcoin ATMs are hard to reverse, which is why scammers ask for them.",
      any: [/\b(bitcoin|btc|usdt|tether|crypto(currency)?|bitcoin atm|crypto atm|wire (transfer|the money)|western union|moneygram)\b/i] },
    { id: "payment-app", weight: 1, article: null,
      label: "Asks for a payment app transfer",
      why: "Zelle, Cash App and Venmo payments work like cash: you usually can't get them back if it's a scam.",
      any: [/\b(zelle|cash ?app|venmo|paypal friends)\b/i] },
    { id: "investment", weight: 3, article: "investment-and-crypto-scams",
      label: "Promises investment returns",
      why: "Big, steady or 'guaranteed' returns, especially from someone you met online, are the hallmark of investment scams.",
      any: [/\b(guaranteed (returns?|profits?|income)|daily (returns?|profits?)|\d+ ?% (returns?|profit|a (day|week|month))|trading (platform|app|signals?)|investment opportunity|mining pool|liquidity pool)\b/i] },
    { id: "wrong-number", weight: 2, article: "investment-and-crypto-scams",
      label: "A friendly 'wrong number' message",
      why: "Many investment and romance scams start with a wrong-number text that turns into a friendship.",
      any: [/\b(wrong number|sorry,? who is this|is this [A-Z][a-z]+\?|nice to meet you anyway|we can be friends)\b/i] },
    { id: "off-platform", weight: 2, article: "romance-scams",
      label: "Wants to move the chat to WhatsApp or Telegram",
      why: "Moving you off a dating app or marketplace means nobody can spot and ban the scammer.",
      any: [/\b(whatsapp|telegram|signal app|text me (at|on)|let'?s (talk|chat|move|continue) (on|over|to)|add (me|our trainer|my manager))\b/i] },
    { id: "toll", weight: 3, article: "toll-texts",
      label: "An unpaid toll notice by text",
      why: "Toll agencies bill through your account or by mail. Texts with a link and a late-fee threat are a common scam.",
      any: [/\b(unpaid toll|toll (balance|bill|charge|fee|services?|notice|violation)|e-?z ?pass|sunpass|fastrak|txtag|peach pass|the toll road)\b/i] },
    { id: "delivery", weight: 3, article: "package-delivery-texts",
      label: "A package problem that needs a link or fee",
      why: "Delivery companies don't text a link asking for an address update or a redelivery fee. Track it from the shop's own email.",
      all: [/\b(package|parcel|shipment|delivery|courier|usps|ups|fedex|dhl|postal|post office)\b/i,
            /\b(on hold|held|failed|unable to deliver|could not be delivered|incomplete|invalid|update (your )?(address|details)|redeliver|reschedul|customs|fee|returned to sender)\b/i] },
    { id: "bank-alert", weight: 2, article: "bank-impersonation-calls",
      label: "A fraud alert asking you to reply or call",
      why: "Fake fraud alerts get you to reply, then a scammer calls pretending to be your bank. Call the number on your card instead.",
      any: [/\b(fraud alert|fraud department|suspicious (activity|transaction|charge|login|sign-?in)|unusual (activity|sign-?in)|did you (attempt|authori[sz]e|make|try)|reply (yes|no|y|n) to)\b/i] },
    { id: "tech-support", weight: 3, article: "tech-support-scams",
      label: "Virus warning with a number to call",
      why: "Real tech companies don't put phone numbers in warnings. The pop-up or call is the scam.",
      any: [/\b(virus|infected|malware|trojan|spyware|your (computer|device|pc) (is|has been) (hacked|locked|compromised)|call (microsoft|apple|windows|tech) support|tech support)\b/i] },
    { id: "fake-order", weight: 4, article: "fake-order-and-refund-emails",
      label: "A charge you didn't make, with a number to call",
      why: "Fake order and renewal emails want you to call. There's no order: check your real account or card statement.",
      all: [/\b(order|purchase|subscription|renewal|invoice|receipt|charged|billed|payment of)\b/i,
            /\b(call|contact|dial|cancel|didn'?t authori[sz]e|did not authori[sz]e|not authori[sz]ed|dispute|refund)\b/i,
            /(\+?1[\s.-]?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}/] },
    { id: "breach-followup", weight: 3, article: "breach-follow-ups",
      label: "Uses a data breach to ask for a fee, code or password",
      why: "Scammers follow breach news with fake fraud calls, settlement 'fees' and dark web scans. Real breach steps are free.",
      any: [/\b(data breach|breach|dark ?web|(class action )?settlement)\b[^\n]{0,100}\b(fee|pay|code|password|verify|scan|call (us|now)|claim now)\b/i,
            /\b(fee|pay|code|password|verify|scan)\b[^\n]{0,100}\b(data breach|dark ?web|breach settlement)\b/i] },
    { id: "government", weight: 2, article: "government-impostor-scams",
      label: "Claims to be a government agency",
      why: "The IRS, Social Security and Medicare don't demand payment by phone or text, or threaten arrest.",
      any: [/\b(irs|internal revenue|social security|ssa|medicare|treasury department|department of (the )?treasury|tax refund|back taxes|federal agent|dmv)\b/i] },
    { id: "prize", weight: 3, article: "prize-and-lottery-scams",
      label: "Says you won a prize",
      why: "Real prizes don't make you pay to collect them, and you can't win a lottery you never entered.",
      any: [/\b(you('ve| have)? (won|been selected)|congratulations[^.?!\n]{0,30}(won|winner|selected)|lottery|sweepstakes|jackpot|claim your (prize|reward|winnings|gift))\b/i] },
    { id: "charity", weight: 2, article: "fake-charity-scams",
      label: "A donation request",
      why: "Check any charity yourself before giving, and never donate by gift card, wire or crypto.",
      any: [/\b(donat(e|ion)|charity|relief fund|families in need|disaster relief|giving tuesday|help (the )?(veterans|children|victims))\b/i] },
    { id: "fake-payment-email", weight: 4, article: "online-marketplace-scams",
      label: "A 'payment pending' notice that needs you to act",
      why: "Payment apps don't hold money until you upgrade your account or pay a fee. Check the app itself, not the email.",
      any: [/\bpayment (is )?(pending|on hold)\b[^\n]{0,120}\b(upgrade|business account|fee|verify|release)/i,
            /\b(upgrade|business account|fee|verify|release)\b[^\n]{0,120}\bpayment (is )?(pending|on hold)\b/i] },
    { id: "marketplace", weight: 2, article: "online-marketplace-scams",
      label: "Marketplace payment or deposit pressure",
      why: "Fake 'payment pending' emails, deposits before you see the item and shipping-label tricks are common marketplace scams.",
      any: [/\b(payment (is )?pending|upgrade (your|to a) (business|premium) account|business account|hold it for you|deposit to hold|shipping label|is (this|it) still available|my (mover|courier|agent) will pick)\b/i] },
    { id: "job", weight: 2, article: "job-and-task-scams",
      label: "Easy remote job you didn't apply for",
      why: "Unexpected job offers with big pay for little work are a top scam. Apply only through a company's real careers page.",
      any: [/\b(remote (job|position|work|opportunity)|work from home|part[- ]time (job|position|work)|recruiter|hiring manager|your (resume|cv|profile) was (recommended|selected)|\$\d[\d,]* ?(-|–|to) ?\$?\d[\d,]* (a|per) (day|daily)|daily (pay|income|salary)|rate products|like videos|boost (sales|apps|products))\b/i] },
    { id: "personal-info", weight: 3, article: "lookalike-links",
      label: "Asks you to confirm personal or bank details",
      why: "Real companies don't ask you to confirm passwords, card numbers or your Social Security number through a message.",
      any: [/\b(confirm|verify|update|enter|provide|re-?enter|validate)\b[^.?!\n]{0,40}\b(ssn|social security number|date of birth|bank (details|info|information|account)|routing number|card (number|details|info)|pin|password|login|credentials|billing (info|information|details))\b/i] },
    { id: "reply-to-activate", weight: 3, article: "toll-texts",
      label: "Asks you to reply so the link works",
      why: "'Reply Y and reopen this message' is a trick to switch on links your phone blocked as spam.",
      any: [/\breply (with )?['"]?(y|yes|1)['"]?\b[^\n]{0,60}\b(link|activate|reopen|re-open|click)/i] },
    { id: "urgency", weight: 2, article: null,
      label: "Rushes you with a deadline",
      why: "Rush is the point: it stops you from checking. Real problems still exist tomorrow.",
      any: [/\b(within|in the next|in) \d+ ?(hours?|hrs?|minutes?|mins?)\b/i,
            /\b(immediately|urgent(ly)?|right away|act now|final (notice|warning|reminder)|last (chance|warning)|expires? (today|tonight|soon)|by (midnight|11:59|end of (the )?day|today)|before it'?s too late)\b/i] },
    { id: "threat", weight: 2, article: null,
      label: "Threatens a penalty",
      why: "Threats of arrest, suspension, shut-offs or late fees are pressure, not how real organisations usually work.",
      any: [/\b(suspend(ed)?|suspension|arrest(ed)?|warrant|legal action|lawsuit|late fee|penalt(y|ies)|deactivat(e|ed|ion)|(account|card) (is |has been |will be )?(locked|frozen|closed|blocked|restricted)|disconnect(ed|ion)?|shut ?off|cut off|licen[cs]e (suspension|revoked))\b/i] },
  ];

  // ---------------------------------------------------------------- link rules
  var SHORTENERS = ["bit.ly", "tinyurl.com", "t.co", "goo.gl", "is.gd", "rb.gy", "cutt.ly", "ow.ly", "tiny.cc",
    "shorturl.at", "s.id", "t.ly", "buff.ly", "rebrand.ly", "bl.ink", "short.io", "v.gd", "qrco.de"];
  var RISKY_TLDS = ["top", "xyz", "icu", "click", "buzz", "cfd", "sbs", "rest", "lol", "cyou", "bond", "monster",
    "quest", "zip", "mov", "gq", "tk", "ml", "cf", "ga", "work", "support", "help", "vip", "win", "loan", "live", "info"];
  var TWO_PART = ["co.uk", "org.uk", "gov.uk", "ac.uk", "com.au", "net.au", "org.au", "co.nz", "co.in", "com.br", "co.jp", "com.mx"];
  // brand word -> real registrable domains
  var BRANDS = {
    usps: ["usps.com"], ups: ["ups.com"], fedex: ["fedex.com"], dhl: ["dhl.com"], amazon: ["amazon.com"],
    paypal: ["paypal.com"], apple: ["apple.com"], icloud: ["icloud.com", "apple.com"], netflix: ["netflix.com"],
    microsoft: ["microsoft.com", "live.com", "office.com"], google: ["google.com"], irs: ["irs.gov"], ssa: ["ssa.gov"],
    medicare: ["medicare.gov"], chase: ["chase.com"], wellsfargo: ["wellsfargo.com"], bankofamerica: ["bankofamerica.com"],
    citi: ["citi.com"], venmo: ["venmo.com"], zelle: ["zellepay.com"], coinbase: ["coinbase.com"], walmart: ["walmart.com"],
    ebay: ["ebay.com"], facebook: ["facebook.com"], instagram: ["instagram.com"], whatsapp: ["whatsapp.com"],
    ezpass: ["e-zpassny.com", "ezpassnj.com", "ezpassva.com", "ezpassmd.com", "e-zpassiag.com"], sunpass: ["sunpass.com"],
    fastrak: ["bayareafastrak.org", "thetollroads.com"], toll: [], tolls: [], txtag: ["txtag.org"]
  };
  var LOOKALIKE = { "0": "o", "1": "l", "3": "e", "4": "a", "5": "s", "rn": "m", "vv": "w" };

  function registrable(host) {
    var parts = host.split(".");
    var last2 = parts.slice(-2).join(".");
    if (TWO_PART.indexOf(last2) >= 0) return parts.slice(-3).join(".");
    return last2;
  }

  function unlook(s) {
    var out = s;
    Object.keys(LOOKALIKE).forEach(function (k) { out = out.split(k).join(LOOKALIKE[k]); });
    return out;
  }

  function findLinks(text) {
    var re = /\b((?:https?:\/\/)?(?:[a-z0-9¡-￿●•*-]+\.)+[a-z¡-￿]{2,24}(?::\d+)?(?:\/[^\s<>"')]*)?)/gi;
    var links = [], m;
    while ((m = re.exec(text))) {
      var raw = m[1].replace(/[.,;:!?]+$/, "");
      if (/^[^\/]*@/.test(raw.replace(/^https?:\/\//i, ""))) continue; // email address, not a link
      if (!/^https?:\/\//i.test(raw) && !/\.(com|net|org|gov|edu|io|co|us|info|top|xyz|icu|click|ly|gd|at|me|app|site|online|shop|store|live|link|vip|support|help|buzz|cfd|sbs|rest|lol|cyou|bond|tk|ml|ga|gq|cf|uk|ca|au|in|win|loan|work|monster|quest|zip|mov)(\/|$|:)/i.test(raw)) continue;
      links.push(raw);
    }
    var ipre = /\b((?:https?:\/\/)?\d{1,3}(?:\.\d{1,3}){3}(?::\d+)?\/[^\s<>"')]*)/gi;
    while ((m = ipre.exec(text))) if (links.indexOf(m[1]) < 0) links.push(m[1].replace(/[.,;:!?]+$/, ""));
    return links;
  }

  function checkLink(raw) {
    var hits = [];
    var url = /^https?:\/\//i.test(raw) ? raw : "http://" + raw;
    var scheme = url.slice(0, url.indexOf(":")).toLowerCase();
    var rest = url.slice(url.indexOf("//") + 2);
    var authority = rest.split(/[\/?#]/)[0];
    var host = authority.split("@").pop().split(":")[0].toLowerCase();
    var reg = registrable(host);
    var tld = host.split(".").pop();
    function add(id, weight, label, why) { hits.push({ id: id, weight: weight, label: label, why: why, article: "lookalike-links", link: raw }); }

    if (authority.indexOf("@") >= 0)
      add("link-at", 4, "Link hides its real address with an @", "Everything before the @ in a web address is ignored. The real site is after it.");
    if (/^\d{1,3}(\.\d{1,3}){3}$/.test(host))
      add("link-ip", 4, "Link goes to a bare number, not a website name", "Real companies use their own domain name, not a raw IP address.");
    if (host.indexOf("xn--") >= 0 || /[^\x00-\x7f]/.test(host.replace(/[●•]/g, "")))
      add("link-punycode", 4, "Link uses look-alike letters", "Some letters from other alphabets look identical to ours. The address isn't what it seems.");
    if (SHORTENERS.indexOf(reg) >= 0 || SHORTENERS.indexOf(host) >= 0)
      add("link-short", 2, "Shortened link hides where it goes", "You can't see the real address. Companies texting about your account rarely use these.");
    if (RISKY_TLDS.indexOf(tld) >= 0)
      add("link-tld", 3, "Unusual web address ending (." + tld + ")", "Scam sites often use cheap endings like ." + tld + ". Banks, agencies and delivery companies don't.");

    var labels = host.split(".");
    var tokens = host.split(/[.\-]/);
    var brandHit = null;
    Object.keys(BRANDS).forEach(function (b) {
      if (brandHit) return;
      var real = BRANDS[b];
      var inReal = real.some(function (d) { return reg === d || host === d; });
      if (inReal) return;
      var exact = tokens.indexOf(b) >= 0 || host.replace(/[.\-]/g, "").indexOf(b) >= 0 && b.length >= 6;
      var looks = tokens.some(function (t) { return t !== b && t.length >= 4 && unlook(t) === b; });
      if (exact || looks) brandHit = { brand: b, looks: looks };
    });
    if (brandHit) {
      if (brandHit.looks)
        add("link-lookalike", 4, "Link imitates a brand name (" + brandHit.brand + ")", "Numbers swapped for letters is a classic look-alike trick.");
      else if (BRANDS[brandHit.brand].length)
        add("link-brand", 4, "Link uses a brand name but isn't its real site", "The real site is " + BRANDS[brandHit.brand][0] + ". This one is " + reg + ", which only borrows the name.");
      else
        add("link-brand", 3, "Link uses a toll word but isn't your toll agency", "Toll agencies have their own sites. Type yours in yourself.");
    }
    if ((reg.match(/-/g) || []).length >= 2)
      add("link-hyphens", 1, "Long, hyphenated web address", "Strings like account-verify-help are typical of scam sites.");
    if (labels.length >= 5)
      add("link-subdomains", 1, "Many dots before the real address", "The real site is the last part, " + reg + ". Everything before it can say anything.");
    if (scheme === "http" && /^https?:\/\//i.test(raw))
      add("link-http", 1, "Link isn't secure (http)", "Not proof of a scam, but real login and payment pages use https.");
    return { link: raw, host: host, domain: reg, hits: hits };
  }

  // ---------------------------------------------------------------- analyse
  function analyze(input) {
    var text = String(input || "").slice(0, 20000);
    var hits = [];
    TEXT_RULES.forEach(function (r) {
      var ok = r.all ? r.all.every(function (re) { return re.test(text); }) : r.any.some(function (re) { return re.test(text); });
      if (ok) hits.push({ id: r.id, weight: r.weight, label: r.label, why: r.why, article: r.article });
    });
    var links = findLinks(text).slice(0, 10).map(checkLink);
    var seen = {};
    links.forEach(function (l) {
      l.hits.forEach(function (h) { if (!seen[h.id]) { seen[h.id] = 1; hits.push(h); } });
    });
    if (links.length && hits.length && !links.some(function (l) { return l.hits.length; }))
      hits.push({ id: "link-unexpected", weight: 1, label: "Contains a link", why: "With the other red flags here, don't tap it. Type the company's address yourself.", article: "lookalike-links" });
    hits.sort(function (a, b) { return b.weight - a.weight; });
    var score = hits.reduce(function (s, h) { return s + h.weight; }, 0);
    var strong = hits.some(function (h) { return h.weight >= 4; });
    var level = score >= 6 || strong ? "high" : score >= 3 ? "medium" : score >= 1 ? "low" : "none";
    var articles = [];
    hits.forEach(function (h) { if (h.article && articles.indexOf(h.article) < 0) articles.push(h.article); });
    var ll = articles.indexOf("lookalike-links");
    if (ll >= 0 && articles.length > 1) { articles.splice(ll, 1); articles.push("lookalike-links"); }
    return { score: score, level: level, hits: hits, links: links, articles: articles };
  }

  var VERDICTS = {
    high: ["Very likely a scam", "This has several of the patterns scammers use. Don't reply, tap the link or pay."],
    medium: ["Red flags found", "Treat this as a scam until you've checked it a safe way."],
    low: ["One warning sign", "Not proof either way. Check it a safe way before you act."],
    none: ["No common red flags found", "That doesn't make it safe. New scams don't always match our patterns."]
  };

  // ---------------------------------------------------------------- page UI
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }

  function render(res, articles) {
    var v = VERDICTS[res.level];
    var html = '<div class="verdict ' + res.level + '"><strong>' + esc(v[0]) + "</strong><p>" + esc(v[1]) + "</p></div>";
    if (res.hits.length) {
      html += '<h2>What we found</h2><ol class="flags">';
      res.hits.forEach(function (h) { html += "<li><strong>" + esc(h.label) + "</strong><br><span>" + esc(h.why) + "</span></li>"; });
      html += "</ol>";
    }
    var reads = res.articles.filter(function (a) { return articles[a]; });
    if (reads.length) {
      html += "<h2>Read the explainer</h2><ul class=\"reads\">";
      reads.slice(0, 3).forEach(function (a) { html += '<li><a href="' + esc(articles[a].url) + '">' + esc(articles[a].title) + "</a></li>"; });
      html += "</ul>";
    }
    html += '<h2>Whatever the result</h2><ul><li>Don\'t tap links or call numbers in the message.</li>' +
      "<li>Contact the company or person yourself, using a number or website you already trust.</li>" +
      "<li>Never share a code, a password, or gift card numbers.</li>" +
      '<li>Already paid or shared details? Call your bank now and report it at <a href="https://reportfraud.ftc.gov/" rel="noopener">ReportFraud.ftc.gov</a>.</li></ul>';
    return html;
  }

  function mount(doc) {
    var form = doc.getElementById("sd-checker");
    if (!form) return;
    var box = doc.getElementById("sd-input"), out = doc.getElementById("sd-result");
    var articles = root.SD_ARTICLES || {};
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      if (!box.value.trim()) { out.innerHTML = "<p>Paste a message or a link first.</p>"; return; }
      out.innerHTML = render(analyze(box.value), articles);
      out.focus();
    });
    form.addEventListener("reset", function () { out.innerHTML = ""; });
  }

  var api = { analyze: analyze, checkLink: checkLink, findLinks: findLinks, render: render, TEXT_RULES: TEXT_RULES, VERDICTS: VERDICTS };
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  else {
    root.SDChecker = api;
    if (root.document) {
      if (root.document.readyState === "loading") root.document.addEventListener("DOMContentLoaded", function () { mount(root.document); });
      else mount(root.document);
    }
  }
})(typeof window !== "undefined" ? window : this);
