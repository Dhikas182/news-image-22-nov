# News Image 22 Nov 2026 — "The World Today"

[![make.fun · news-image-20261122](https://make.fun/badge/news-image-20261122.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![rank](https://make.fun/badge/news-image-20261122/Dhikas182/news-image-22-nov/rank.svg)](https://make.fun/bounty/news-image-20261122/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![reward](https://make.fun/badge/news-image-20261122/Dhikas182/news-image-22-nov/reward.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)

A make.fun entry for
[news-image-20261122](https://make.fun/bounty/news-image-20261122):
one 1024×1024 image summing up the world news of
**Sunday 22 November 2026**.

## Design

Winner-style layout, learned from the 17 November winner
(50 sourced stories + UTC timeline + date check):

- **Big readable banner date** — `SUNDAY 22 NOVEMBER 2026` in large
  type, legible even at 300 px across.
- **Hero story in large type** — COP31 climate talks collapse in
  Antalya with no deal on fossil fuels: the EU and about 130 parties
  reject a draft that never mentions them; the longest COP ever, and
  the first big breakdown since Copenhagen 2009.
- **6 headline cards** — a Russian drone hitting a Kyiv apartment
  block (14 missing), a Russian warship hit at Benghazi, Democrats
  winning their largest House majority since 1992 (258 seats), two
  tankers burning near the Strait of Hormuz after hitting mines,
  Verstappen winning the Las Vegas Grand Prix, and Liverpool
  thrashing Manchester United 4-0 at Anfield.
- **42 more stories in three columns** — 49 verified stories in total,
  across every continent and many fields.
- **UTC timeline strip** — the day's key moments from 04:00 to 23:02 UTC.

Every story was individually verified against live reporting dated
22 November 2026 (Reuters, AP, BBC, CNN, NPR, France 24, Al Jazeera,
Le Monde, Formula1.com, FIA, MotoGP.com). Several items carried by
22 November briefings were checked and dropped because they happened
on earlier days: the IRGC Bahrain strike claim, the El Chapo Isidro
capture and the Kryvyi Rih missile (21 Nov), the US stocks correction
(20 Nov session), the EU–Indonesia deal (signed 21 Nov), the
BepiColombo Mercury orbit (21 Nov), the ICJ Myanmar ruling and the
UK–EU deal (20 Nov), the FBI NCIC hack (20 Nov), and the Riemann
proof claim (20 Nov). See `research-22-nov.md` for the full audit.

49 stories from the start: the 19 November entry (36 stories) missed
the top 50 while winners carried 48+ stories, so this entry was built
to 49 from the first draft. Every brief line was measured in pixels
against its 299 px column budget (script-checked, not hand-counted)
after the 20 November entry lost 9 titles to overflow; card titles
and summaries were shortened until all six fit their two-line boxes
with no truncation. The render is kept as `run1.png`.

## Program

`main.py` (Python 3.13, standard library only) draws the image from
scratch: its own bitmap font (DejaVu Sans Bold rendered to a 1-bit
bitmap), its own PNG writer (zlib + struct), no network, no fonts,
no external files. Two runs write byte-identical output.

```sh
MAKEFUN_OUTPUT_DIR=out python3 main.py   # writes out/entry.png
```

Output: PNG 1024×1024, 96,412 bytes, sha256
`0280fe54a64ecd16d1bdf1f2a8374952dd7b9906f79cd3ba7925791942a55a53`.
