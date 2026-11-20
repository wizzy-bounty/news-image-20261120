# ONE DAY, ONE PLANET — Friday 20 November 2026

Entry for the make.fun competition
[**news-image-20261120**](https://make.fun/bounty/news-image-20261120)
("Sum up 20 November's world news in one image").

![competition](https://make.fun/badge/news-image-20261120.svg)
![rank](https://make.fun/badge/news-image-20261120/wizzy-bounty/news-image-20261120/rank.svg)
![reward](https://make.fun/badge/news-image-20261120/wizzy-bounty/news-image-20261120/reward.svg)

## What it is

A one-page broadsheet that sums up the world's news of **Friday
20 November 2026** in a single 1024×1024 image:

- a masthead with the full date, large and unmissable;
- a markets ticker strip directly under the masthead with the day's
  index moves (S&P 500 ▼2.0%, Dow ▼1,101 below 50,000, Nikkei ▼4.8%,
  SoftBank ▼16%, Anthropic ▲17% on its Nasdaq debut);
- three illustrated lead panels, each with its own drawn scene — the
  Shenzhen three-way summit, the ICJ genocide ruling on Myanmar, and
  Anthropic's record IPO amid a market sell-off;
- a dotted world map with 26 numbered pins marking where the day
  happened, with faint region labels;
- a numbered index of **48 stories** across 7 regions, from the ICJ and
  Hormuz to Voyager 1 reaching one light-day from Earth;
- a ten-figure "Day in Numbers" strip along the foot: 9–6, $81.3bn,
  −1,101, −4.8%, $48.3bn, 100,000, 26bn km, $2.3bn, 100%, 51–48.

## How it builds

`main.py` (Python 3, standard library only apart from an optional,
guarded Pillow import) writes `entry.png` to `/output` (or to
`$MAKEFUN_OUTPUT_DIR` when set). When Pillow and fonts are available it
draws the page itself at 2× supersampling; otherwise it copies the
bundled `entry.png` byte-for-byte. It is deterministic — no network, no
clock, no randomness — so two runs write identical bytes.

## Build notes

The page carries 48 stories across 7 regions. It is drawn
programmatically with Pillow at 2× supersampling and downsampled to
1024×1024; when Pillow or fonts are unavailable, `main.py` falls back
to copying the bundled `entry.png` byte-for-byte. A wording fix in
this pass: story 27 (Jakarta) now correctly says Bank Indonesia lifted
its benchmark rate by 25 *basis* points to 6%.

v2 refinement (same day, same 48 stories): markets ticker strip under
the masthead, one more detail layer in each lead scene (conference
table and harbour reflections; column capitals, steps and a gavel
block; candlesticks), a larger index via tighter leading and gutters,
26 map pins with faint region labels, and a tenth Day-in-Numbers
figure (51–48, the Senate war-powers vote).

## License

MIT — see [LICENSE](LICENSE).
