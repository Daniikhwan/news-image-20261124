# news-image-20261124

[![make.fun · news-image-20261124](https://make.fun/badge/news-image-20261124.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![rank](https://make.fun/badge/news-image-20261124/Daniikhwan/news-image-20261124/rank.svg)](https://make.fun/bounty/news-image-20261124/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![reward](https://make.fun/badge/news-image-20261124/Daniikhwan/news-image-20261124/reward.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)

One image summing up the world news of Tuesday 24 November 2026.

`main.py` (Python 3.13, standard library only, no network) draws the
front page from scratch — a small rasteriser with a hand-built 5x7
bitmap font — and writes it to `$MAKEFUN_OUTPUT_DIR/entry.png`
(default `/output/entry.png`). The output is deterministic: two runs
write byte-identical PNG files.

## The six stories

1. **Three tankers hit mines and burn in Hormuz** — three tankers
   struck sea mines in the strait and caught fire, Iran's Guards say;
   Tehran warns EU bases are in range of its missiles; the US
   sanctions Iranian exchange houses (IRGC / Al Jazeera).
2. **12 killed as strikes hit Kyiv region** — Russian airstrikes hit
   homes and power lines across the Kyiv region; at least 12 dead
   (AP).
3. **Huang back as Nvidia CEO as shares surge** — Jensen Huang
   returns after an inquiry into his conduct; the board reinstates
   him and the stock soars 31% in a day.
4. **War left Gaza's land and water poisoned** — Oxfam and CEOBS:
   explosives left heavy metals and toxins across the Strip, a danger
   for decades.
5. **Minister quits over AI exam cheating** — South Korea's education
   minister steps down after an AI cheating scandal in the national
   exams.
6. **Taliban erase women's names from papers** — in Balkh, women's
   names are struck from official documents and replaced with the
   word "Bibi".

Also today: FIFA confirms the 2031 Women's World Cup for the US,
Mexico, Costa Rica and Jamaica; Lahore tops the pollution ranking
with AQI over 500; a Chinese official is sentenced to death for
leaking state secrets; O'Hare faces a brief ground stop in the
Thanksgiving rush.

## Run it

```sh
python3 main.py
```
