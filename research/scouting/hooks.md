# 30 hook templates

The library lives at `src/contentfactory/hooks_library.json`, so the pipeline uses it directly:
`contentfactory/hooks.py` loads it, and for brands whose niche matches (finance, money, scams...) the
writer's prompt gets 4 templates that fit the title's topic and the format, each with a different
mechanic. The model uses them as inspiration for `hook` and `hook_variants`, and fills them with the
script's specifics. Turn it off with `FACTORY_HOOK_LIBRARY=0`.

Rules the templates follow (tests enforce the first two):
- No guarantee, get-rich, risk-free, engagement-bait or fake-testimonial wording (`guardrails.py` patterns).
- Every `{slot}` in a pattern is declared; a template with a number to verify sends that number to the fact-check list.
- Second person or "we", never "I used this": the presenter is faceless.
- Share prompts give a real reason ("send this to your parents before..."), never "tag 3 friends".

Use from code:

```python
from contentfactory.hooks import load_library
lib = load_library()
lib.get("stop-doing").render(common_habit="budgeting monthly", better_habit="budgeting by paycheck")
lib.suggest("Freeze your credit for free", "short", k=4)
```

| id | Mechanic | Pattern | Formats | Number to verify |
|---|---|---|---|---|
| `fine-print` | insider secret | {company_type} won't tell you this, but it's in the fine print: {hidden_rule}. | short, carousel |  |
| `cost-of-mistake` | loss aversion with a number | This one {setting} costs the average {person} {amount} a year. | short, carousel | yes |
| `if-i-started-today` | restart / dated frame | Starting {goal} from zero in {year}? Here's the exact order to do it in. | short, long, carousel |  |
| `visualize-the-number` | visual payoff | This is what {amount} {timeframe} turns into after {years} years. | short, carousel | yes |
| `x-vs-y-real-math` | comparison with proof | {option_a} or {option_b}? We ran the real numbers on {scenario}. | short, carousel, long | yes |
| `stop-doing` | contrarian instruction | Stop {common_habit}. Do {better_habit} instead. | short, carousel |  |
| `myth-check` | myth vs fact | "{myth}." That's the most expensive money myth I hear. Here's why. | short, carousel |  |
| `tonight-in-minutes` | low-effort action | Do this tonight. It takes {minutes} minutes and {benefit}. | short |  |
| `three-signs` | numbered list with an open loop | {n} signs {situation}, and the last one surprises most people. | short, carousel |  |
| `pov-your-age` | identity / self-selection | You're {age}, earning {salary}. Here's where every dollar should go. | short, carousel | yes |
| `nobody-explains` | promise of clarity | Nobody explains {topic} like this, so here it is in {seconds} seconds. | short |  |
| `word-on-statement` | document anchor | If you see "{term}" on your {document}, read this first. | short, carousel |  |
| `free-money-left` | found money | You're probably leaving {benefit} on the table, and it's free to claim. | short, carousel |  |
| `same-income-different-result` | social comparison | Two people earn {salary}. One ends up with {result_a}, the other with {result_b}. The only difference is {difference}. | short, carousel | yes |
| `the-one-question` | decision shortcut | {decision}? Answer one question and you'll know. | short, carousel |  |
| `paid-off-but` | unexpected outcome | You {did_the_right_thing} and {bad_outcome} anyway. Here's why that happens. | short |  |
| `app-honest-review` | curation / tested so you don't | We compared {n} {category} on {criteria}. Only {winner_count} passed. | carousel, long |  |
| `calendar-surprise` | reframe | That '{surprise}' wasn't a surprise. It was on the calendar. Here's how to see it coming. | short, carousel |  |
| `percent-fee-eats` | hidden cost reveal | A {fee} fee sounds tiny. Over {years} years it eats {amount}. | short, carousel | yes |
| `checklist-save` | utility / save prompt | The {n}-step {task} checklist. Save this for {moment}. | carousel |  |
| `what-you-own` | demystify | When you buy {product}, here's what you actually own. | short, carousel |  |
| `scam-script-reveal` | pattern reveal | This is the exact script {scammer_type} use, line by line, so you'll recognise it. | short, carousel, long |  |
| `scam-one-tell` | single rule to remember | Every {scam_type} has the same tell: {tell}. | short, carousel |  |
| `scam-real-or-fake` | interactive quiz | Real or scam? {artifact}. You have 3 seconds. | short, carousel |  |
| `scam-what-happens-next` | consequence timeline | You {mistake}. Here's what happens in the next {hours} hours, and how to stop it. | short, carousel |  |
| `scam-too-good` | follow the money | "{offer}." Here's how this offer actually makes its money. | short, long |  |
| `scam-protect-parents` | share to protect | Send this to {person} before {scam_type} reaches them. | short, carousel |  |
| `small-change-big-year` | tiny habit, concrete total | One {small_change} a {period} adds up to {amount} by next {month}. | short, carousel | yes |
| `question-you-asked` | Q&A / reply format | Someone asked: "{question}" Honest answer: {short_answer}. | short |  |
| `boring-wins` | anti-hype | The most boring {thing} is also the one that {result}. | short, carousel |  |

Where they come from: [`creators.md`](creators.md).
