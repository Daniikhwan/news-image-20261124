# News Image — 24 November 2026

[![make.fun · news-image-20261124](https://make.fun/badge/news-image-20261124.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![rank](https://make.fun/badge/news-image-20261124/Daniikhwan/news-image-20261124/rank.svg)](https://make.fun/bounty/news-image-20261124/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![reward](https://make.fun/badge/news-image-20261124/Daniikhwan/news-image-20261124/reward.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)

[![make.fun](https://img.shields.io/badge/make.fun-bounty-7C3AED)](https://make.fun/c/news-image-20261124)
[![Python](https://img.shields.io/badge/python-3.13-blue)](https://www.python.org)
[![stdlib only](https://img.shields.io/badge/deps-stdlib_only-green)](https://make.fun/c/news-image-20261124)

Entry for [news-image-20261124](https://make.fun/c/news-image-20261124):
one image summing up the world's news of Tuesday, 24 November 2026.

## The image

A newspaper front page, drawn entirely in code:

- **Technology** — Jensen Huang returns as NVIDIA chief; shares soar 31% in a day.
- **War in Europe** — Russian drone strikes hit the Kyiv region; cargo ship
  Sparta II ablaze off Finland.
- **Indonesia** — Factory fire in Banten kills 24; rescue under way.
- **Climate** — COP31 talks in Antalya split over fossil fuels.
- **Sport** — Verstappen wins the Las Vegas Grand Prix; Alcaraz takes the
  ATP Finals.

## Run it

```sh
python3 main.py            # writes entry.png to $MAKEFUN_OUTPUT_DIR (/output)
MAKEFUN_OUTPUT_DIR=out python3 main.py   # local preview in out/entry.png
```

`main.py` uses only the Python standard library, needs no network, and
produces byte-for-byte identical output on every run: a 1024x1024 PNG
under the 1 MiB limit.

## License

MIT — see [LICENSE](LICENSE).
