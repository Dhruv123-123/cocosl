// Page copy for each calculator. `node build.mjs` turns this into static HTML pages.
// Each page targets one search query and answers it in plain English under the tool.
export const pages = [
  {
    slug: 'debt-payoff',
    title: 'Debt Payoff Calculator: Avalanche vs Snowball',
    h1: 'Debt payoff calculator: avalanche vs snowball',
    description: 'Enter your debts and see your debt-free date, total interest, and how much the avalanche method saves compared with the snowball.',
    intro: 'List what you owe. We run both payoff orders month by month and show your debt-free date and the interest each one costs.',
    faq: [
      ['What is the avalanche method?', 'Pay the minimum on everything, then put every extra dollar on the debt with the highest APR. When it is gone, roll that payment to the next-highest. It costs the least interest.'],
      ['What is the snowball method?', 'Same idea, but you target the smallest balance first. You pay a little more interest, but you clear whole debts sooner, which keeps many people going.'],
      ['Which one should I use?', 'The one you will stick with. If avalanche saves only a few dollars, snowball is fine. If it saves hundreds, it is usually worth the patience.'],
    ],
  },
  {
    slug: 'compound-interest',
    title: 'Compound Interest Calculator with Monthly Contributions',
    h1: 'Compound interest calculator',
    description: 'See how a starting amount plus a monthly contribution could grow over time, and how much of the total is growth rather than money you put in.',
    intro: 'Pick a starting amount, a monthly contribution and a yearly return. The chart shows how growth overtakes what you put in.',
    faq: [
      ['What return should I use?', 'Broad US stock index funds have averaged roughly 7% a year after inflation over long periods, with big swings in between. Use a lower number to be cautious. Past returns do not guarantee future ones.'],
      ['Why does starting early matter so much?', 'Growth earns growth. Money invested in your twenties has decades longer to compound than money added later, so small early amounts often end up larger.'],
      ['Does this include fees or taxes?', 'No. Subtract your fund expense ratio from the return to include fees, and use a tax-advantaged account like a 401(k) or IRA to reduce tax drag.'],
    ],
  },
  {
    slug: 'emergency-fund',
    title: 'Emergency Fund Calculator: How Much and How Long',
    h1: 'Emergency fund calculator',
    description: 'Work out how big your emergency fund should be and how many months it will take to build it, with interest from a high-yield savings account.',
    intro: 'Add up the bills you can\'t skip (rent, food, transport, insurance, minimum debt payments), pick how many months to cover, and see your timeline.',
    faq: [
      ['How many months should I save?', 'Three months of essential costs is a common target, six if your income is irregular or you support others. Start with a $1,000 starter fund.'],
      ['Where should I keep it?', 'In a separate, FDIC or NCUA insured savings account you can reach in a day or two, but not with your spending card.'],
      ['Should I pay off debt first?', 'Many people build a small starter fund first so a surprise bill does not go on a credit card, then attack high-interest debt, then finish the full fund.'],
    ],
  },
  {
    slug: 'savings-interest',
    title: 'High-Yield Savings Calculator: How Much Interest Will I Earn?',
    h1: 'High-yield savings interest calculator',
    description: 'Compare the interest a high-yield savings account pays with a typical big-bank savings account, based on your balance and monthly deposits.',
    intro: 'Most big-bank savings accounts pay close to nothing. Put in your balance and see what a higher APY would add.',
    faq: [
      ['What is APY?', 'Annual percentage yield: the yearly return including compounding. A 4% APY on $10,000 earns about $400 in a year if the rate stays the same.'],
      ['Are high-yield savings accounts safe?', 'Ones at FDIC insured banks or NCUA insured credit unions are protected up to $250,000 per depositor, per bank, per ownership category. Check the insurance before you open one.'],
      ['Do rates change?', 'Yes. Savings rates are variable and usually move with the Federal Reserve\'s rate. Re-check every few months.'],
    ],
  },
  {
    slug: 'credit-card-minimum',
    title: 'Credit Card Minimum Payment Calculator',
    h1: 'Credit card minimum payment calculator',
    description: 'See how long paying only the minimum on a credit card takes and how much interest it costs, compared with a fixed monthly payment.',
    intro: 'Minimum payments are designed to shrink as your balance does, which stretches the debt out for years. See the real cost.',
    faq: [
      ['How is the minimum payment calculated?', 'Commonly the interest for the month plus 1% of the balance, with a floor such as $25 or $35. Your card agreement has the exact formula.'],
      ['Why does a fixed payment help so much?', 'A fixed amount does not shrink as the balance falls, so more of each payment goes to principal every month.'],
      ['What about a balance transfer?', 'A 0% transfer can help if the fee is small and you clear the balance before the promo ends. Do not add new spending to the old card.'],
    ],
  },
  {
    slug: 'take-home-pay',
    title: 'Take-Home Pay Calculator 2026: Salary After Taxes',
    h1: 'Take-home pay calculator (2026)',
    description: 'See what a salary pays per paycheck after 2026 federal income tax, Social Security, Medicare, state tax and pre-tax 401(k) or health premiums.',
    intro: 'Enter your salary and pre-tax deductions. We apply the 2026 federal brackets, the standard deduction, Social Security and Medicare, plus your state rate.',
    faq: [
      ['Why is my paycheck smaller than salary divided by paychecks?', 'Federal income tax, Social Security (6.2%), Medicare (1.45%), state tax and any pre-tax deductions all come out first.'],
      ['Does a 401(k) lower my taxes?', 'Traditional (pre-tax) 401(k) contributions lower your federal and usually state income tax, but not Social Security or Medicare. Roth 401(k) contributions don\'t lower today\'s tax.'],
      ['What is my tax bracket?', 'Your bracket is the rate on your last dollar of taxable income. Lower slices of income are taxed at lower rates, so your overall (effective) rate is lower than your bracket.'],
    ],
  },
  {
    slug: 'roth-vs-traditional',
    title: 'Roth vs Traditional IRA and 401(k) Calculator',
    h1: 'Roth vs Traditional calculator',
    description: 'Compare the after-tax value of Roth and Traditional retirement contributions using your tax rate now and your expected rate in retirement.',
    intro: 'Same pre-tax dollars, two tax treatments. The answer comes down to one question: is your tax rate higher now, or later?',
    faq: [
      ['When does Roth win?', 'When your tax rate in retirement is higher than it is today, which is common for students and early-career workers in low brackets.'],
      ['When does Traditional win?', 'When you are in a high bracket now and expect a lower rate in retirement. You get the tax break up front.'],
      ['Can I do both?', 'Yes. Splitting contributions is a reasonable hedge when you are unsure about future tax rates. Check the IRS income and contribution limits for the year.'],
    ],
  },
];
