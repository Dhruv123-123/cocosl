---
alert_date: 2026-11-16
severity: watch
scam: Gift cards drained before you even give them
channel: store rack
sender: a gift card that was tampered with on the shelf
subject: Scam alert: the gift card that's empty on arrival
preheader: Check the package and the PIN strip before you pay, and keep the receipt.
example: The card on the rack looks normal, but the PIN strip has been peeled and re-covered, and the barcode has a sticker over it. You load $100. A week later it's empty.
flags: PIN strip has been peeled | barcode has a sticker over it | A week later it's empty
tell_1: A scratched, peeled or re-stuck PIN strip on the back.
tell_2: A torn or resealed package, or a second barcode sticker on top of the real one.
tell_3: The balance is gone before the person you gave it to ever used it.
do_1: Check the package and the PIN area before you pay. Pick one from the back of the rack.
do_2: Keep the receipt with the card, and give both together.
do_3: Empty card? Call the brand on the card right away with the receipt, then report it at ReportFraud.ftc.gov.
if_already: Card already drained? Contact the gift card company now, using the number on the back, and ask about a refund. Keep the receipt.
source_title: FTC: Check out gift cards before you buy them
source_url: https://consumer.ftc.gov/consumer-alerts/2024/12/check-out-gift-cards-you-buy-them
explainer: gift-card-scams
---
