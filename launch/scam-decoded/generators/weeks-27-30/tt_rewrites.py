"""TikTok cuts reword their Short's beats instead of repeating them (originality audit: repeated sentences).
Short title -> new narration for the Short's 4 beats, in order (hook line, beat 2, beat 3, last beat)."""

TT = {
    "'Free' Medicare genetic test: 1 swab, 1 stolen number": [
        "It's sold as a free cheek swab that Medicare pays for, offered on the phone, at a booth, or on your doorstep.",
        "The kit needs your Medicare number to ship, and that number is the real prize. It gets billed for a test nobody needed, and it can be billed again later.",
        "And when Medicare turns the claim down because no doctor of yours asked for it, you can end up holding the bill.",
        "So the only test you take is one your doctor ordered. Your Medicare number stays with you, whoever's asking.",
    ],
    "'Your doctor approved a free back brace': hang up": [
        "The call opens with a question: any pain in your back or knees? Good news, a brace is covered and costs you nothing.",
        "All they need is your Medicare number for shipping. Then a brace shows up you never needed, Medicare pays for it, and your number is passed along to others.",
        "Your doctor doesn't phone you to sell braces, and neither does Medicare. Wanting your number is the whole scheme.",
        "End the call. If an unordered box turns up, don't accept it, and report it by calling 1-800-MEDICARE.",
    ],
    "A 'courier' at Grandma's door: 1 scam twist to know": [
        "The voice cries: it's me, there was a crash, they've locked me up, I need bail, and please keep it from Mom.",
        "The new part: nobody asks for a wire or gift cards. A man just turns up at your door to take the cash.",
        "Bail offices, courts and lawyers don't send people door to door for cash. And a voice that sounds just like family is easy to fake today.",
        "End the call and ring your grandchild or their mom or dad on a number you trust. Then set a family safe word together.",
    ],
    "'Interview on Telegram today': 1 job offer to walk away from": [
        "The whole interview happens in a chat app, by text, and sixty minutes later you get the job.",
        "Then they mail you a check for your work laptop, and tell you to pay their approved vendor out of it.",
        "A few days on, the check is fake. Your bank pulls back the deposit, and the money you sent the vendor doesn't come back.",
        "A real company meets you on video or face to face, and won't send you a check to buy your own equipment.",
    ],
    "'You won a scholarship, pay the fee': 0 real ones charge": [
        "Not one genuine scholarship charges you to apply or to collect. Here's how the fakes sound.",
        "You've won an award you don't remember applying for, and there's a small fee to process it.",
        "Or someone wants money to do your FAFSA, or sells a promise of aid for a fee. The FAFSA costs nothing and you can file it on your own.",
        "Your school's financial aid office will help for free. Paying to get free money is the red flag.",
    ],
    "'I'm abroad, can't show you the apartment': 1 rental flag": [
        "Here's the sentence that should end it: the landlord's overseas, can't let you in, but wants a deposit to hold the place.",
        "The pictures are lifted from a real ad, the rent is suspiciously low, and others are supposedly about to pay, so hurry.",
        "Renters told the FTC they lost sixty-five million dollars to scams like this, and many never report it at all.",
        "No money changes hands until you, or a person you trust, has walked through it and met whoever's renting it.",
    ],
    "'A bigger VA pension, for a fee': 1 offer to refuse": [
        "It starts with a free lunch about VA pensions, and ends with a fee and a plan to put your savings in an annuity.",
        "They say they'll get you a bigger pension quickly, bill you for paperwork, and sell products that tie up your money for years.",
        "Accredited representatives help with VA claims for free. A fee, or an investment pitch, is how you spot the scheme.",
        "Search VA's own site for an accredited representative, or go through a veterans service organization.",
    ],
    "'Help veterans this Memorial Day': a 2-minute check": [
        "Before you give to a veterans' group this weekend, take two minutes. Which of these should worry you?",
        "A name that's nearly a famous charity's. Pressure to give before you hang up. A request for gift cards or a wire.",
        "Every one of them. A real charity will still take your donation next week, and never by gift card or wire.",
        "Find the charity on your own, check a watchdog like Give.org or Charity Navigator, and donate on its own site.",
    ],
    "'Deployed, can't video call': 4 tells of a fake soldier": [
        "Here are four signs a soldier's profile is fake. First: they're deployed, so a video call is never possible.",
        "Second, it's love and marriage talk within weeks. Third, they push you off the app to WhatsApp or email.",
        "Fourth, money: for leave, a ticket home, a parcel, or to end the deployment early. The military doesn't work like that.",
        "Run their photos through a reverse search, stay on the app, and don't send money to anyone you've never met.",
    ],
    "'Flight canceled, call to rebook': 1 text to check first": [
        "The text says your flight's cancelled and gives you a number to call to rebook.",
        "Someone helpful books you a new seat, charges a fee to your card, and the new ticket never arrives.",
        "That number came from a text, not your airline's app or confirmation. Scammers buy ads for fake airline help lines too.",
        "Check in the airline's app, or on the site you typed in. That's where your real status is.",
    ],
    "That 'official' hotel site: 1 check before you book": [
        "A search ad copies the hotel's site perfectly: the same pictures and a lower rate.",
        "You book and get a confirmation the hotel can't find, or fees pile up at checkout until the price doubles.",
        "Read the address bar. If it's not the hotel's own address, you're on a reseller at best, a fake at worst.",
        "Type the hotel's address in yourself, phone the front desk to confirm, and use a credit card.",
    ],
    "Road trip? 1 tug at the gas pump spots a skimmer": [
        "Give the card reader one tug before you pay for gas. Here's the reason.",
        "A skimmer copies your card. Some fit over the reader, others hide inside the pump behind a tampered seal.",
        "Pull on the reader, look at the tape on the pump door, and use a pump the cashier can see.",
        "Even better, tap or pay at the counter. Pay with credit instead of debit, and switch on alerts for your card.",
    ],
}
