"""TikTok cuts reword their Short's beats instead of repeating them (originality audit: repeated sentences).
Short title -> new narration for the Short's 4 beats, in order (hook line, beat 2, beat 3, last beat)."""

TT = {
    "'Send $50, get $500': 1 money flip that only goes one way": [
        "The post promises to turn fifty dollars into five hundred, with screenshots, a countdown and only a few spots left.",
        "Nothing gets flipped. The fifty disappears the moment you send it, and then a message says your five hundred is waiting behind a release fee.",
        "No one can grow money you send to a stranger. Payment apps don't run pay-first giveaways, and those screenshots are made up.",
        "Keep scrolling. Use payment apps only with people you know, and if a friend's account posts one, message them somewhere else to say they've been hacked.",
    ],
    "'Free game coins, just log in': 1 site that takes accounts": [
        "Your kid sees a video: endless free coins, just type in your username and password.",
        "No generator exists. The site keeps the login, then the account, the skins, and everything bought with real money are taken.",
        "Games sell their currency inside the game or on gift cards. A site handing it out for your password is a scam every time.",
        "Teach the rule: the password only goes into the game itself. Then set up two-step verification and a parent PIN side by side.",
    ],
    "'Babysitting, $600 a week, check first': 1 offer to refuse": [
        "A babysitting job arrives by text: six hundred a week, and they'll post you a check before you've even met.",
        "The check is bigger than your wages. Keep your pay, they say, and send the rest to a supplier for baby gear.",
        "The bank shows the money, so it looks fine. Then the check bounces, and every dollar you sent is yours to repay.",
        "Meet the family on video and then in person. Never forward money from a check, and remember real jobs pay after the work.",
    ],
    "'Your car warranty is about to expire': 1 call to hang up on": [
        "The robocall calls it your final notice: your car's warranty is ending, press one for a specialist.",
        "This isn't the carmaker or the dealer. It's a service contract seller, and some take a deposit and vanish.",
        "They can't name your car, they need payment today, and pressing one only brings more calls.",
        "End the call. Your manual or your dealer can say what coverage you have, and any extra is a decision to compare in writing.",
    ],
    "'Removed from Google today': 1 robocall business owners get": [
        "A recording says your business comes off Google today unless you press one to verify.",
        "A live person then offers to fix it, or to rank you first, for a fee. Some are pushy sales, some are outright scams.",
        "Claiming and running a basic Google Business Profile costs nothing. The deadline is a pressure tactic.",
        "Hang up and sign in to your profile yourself to see that it's fine. Send this to a friend who runs a shop.",
    ],
    "Selling Dad's truck? 1 'buyer' who overpays by check": [
        "A buyer offers the full price for Dad's truck, sight unseen, and mails a check for two thousand more than you asked.",
        "Please wire the extra to my shipper, who'll collect the truck, they say. The check looks flawless.",
        "Then the check bounces. The two thousand you wired is lost, and sometimes the truck goes with it.",
        "Sell to someone who sees the truck and pays in a way you can check, like at your own bank. Never refund an overpayment.",
    ],
    "'You missed jury duty, there's a warrant': courts don't call": [
        "The caller says you skipped jury duty, a warrant is out, and you can settle the fine right now.",
        "He sounds official, reads a badge number, and wants a payment app, gift cards or a prepaid card to clear it.",
        "The federal courts say they don't phone people demanding fines, and won't ask for your card or Social Security number that way.",
        "End the call, find the court's number on its official website, and ask them directly.",
    ],
    "'Cloud storage full, photos deleted': check Settings instead": [
        "The email warns your storage is full and your photos and videos are about to be wiped, unless you upgrade at a special discount.",
        "The button opens a copycat page that collects your card, and sometimes your account password as well.",
        "Panic about photos, a deadline, a deal you didn't request. Genuine storage warnings appear in your phone's settings.",
        "Skip the link. Go to Settings, tap your name, then storage, and read the real figure.",
    ],
    "'Your deed copy for $89': 1 official-looking letter": [
        "The letter has a seal, your parcel number, a ten-day deadline, and an offer of a certified deed copy for eighty-nine dollars.",
        "Stop for a second. Is this from the government, or is a company selling you something? Find the fine print.",
        "It's a company, and the fine print admits it isn't a government agency. The county recorder keeps your deed, often free online or for a few dollars.",
        "Skip it. Need a copy? Use your county recorder's own site. And look through your parents' mail for letters like this.",
    ],
    "'I found your dog, send me a code': 1 lost pet text to stop": [
        "Minutes after your lost dog flyer goes up: I may have your dog, I'll text you a code, send it back to prove you're the owner.",
        "That code is from a service setting up an account with your phone number, which they'll use for other scams.",
        "A real finder sends a photo or meets you. They never need a code or money up front.",
        "Don't share codes. Ask for a fresh photo with an object you choose, and meet somewhere public with a friend.",
    ],
    "'I sent you $300 by mistake': 1 payment to leave alone": [
        "Three hundred dollars arrives from a name you don't know, then a message: oops, wrong person, could you send it back?",
        "That money came from a stolen account and will be pulled back. What you sent from your own balance won't be.",
        "Watch for it: a stranger, polite urgency, and a push to send it yourself instead of going through the app.",
        "Leave it alone. Reach the app's support from inside the app, and let the app return it.",
    ],
    "Famous face selling a 4th of July deal? 1 check first": [
        "An ad shows a celebrity pushing a holiday sale on something they supposedly use daily, at seventy percent off.",
        "The clip might be AI-made, or the face used without permission, and the shop may never send anything.",
        "Search the star's name with the product. A real endorsement shows up on their own pages, not just in ads.",
        "Keep scrolling and report the ad. The menu is right here, and it takes two taps.",
    ],
}
