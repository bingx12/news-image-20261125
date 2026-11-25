# news-image-20261125

[![make.fun · news-image-20261125](https://make.fun/badge/news-image-20261125.svg)](https://make.fun/bounty/news-image-20261125?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)
[![rank](https://make.fun/badge/news-image-20261125/bingx12/news-image-20261125/rank.svg)](https://make.fun/bounty/news-image-20261125/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)
[![reward](https://make.fun/badge/news-image-20261125/bingx12/news-image-20261125/reward.svg)](https://make.fun/bounty/news-image-20261125?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)

THE WORLD TODAY — a pure-stdlib Python program that draws Wednesday 25 November 2026's world news as a one-page newspaper front page and writes it to `/output/entry.png` (1024×1024 PNG, under 1 MiB, byte-identical on every run).

## Run it

```sh
python3 main.py
```

No network, no clock, no randomness: `main.py` renders everything itself from bitmap glyphs in `font_data.py` (DejaVu Sans Book and Bold at one 64px base size, scaled at runtime with stroke-preserving sampling) and encodes the PNG with `zlib`.

## The day's stories

Every story on the page happened or was first reported on Wednesday 25 November 2026 (Reuters, AP, BBC, Xinhua, pm.gov.au):

- **Lead — Pakistan reaches orbit.** China's Shenzhou-24 lifts off from Jiuquan at 00:18 UTC carrying Tang Hongbo, Wu Yi and Pakistan's Muhammad Zeeshan Ali — the first Pakistani, and the first foreign astronaut, to visit China's Tiangong station. The crew docks at 11:56 Beijing time.
- **The Pacific.** Australia and Solomon Islands sign a historic treaty in Canberra: Honiara names Australia its primary security partner and vows no foreign military base on its soil, letting its 2022 security pact with China lapse.
- **Justice.** A Brooklyn jury finds Huawei guilty on 10 of 12 counts — bank fraud, wire fraud, sanctions violations and conspiring to steal trade secrets, including Cisco router code. Sentencing is set for September 2027.
- **Markets.** Nvidia falls about 7% as lawmakers question President Trump's role in reinstating Jensen Huang; Tokyo's Nikkei slides 2.76% and SoftBank plunges 15% as doubts over the AI boom spread.
- **Europe.** Pedro Sanchez and Alberto Nunez Feijoo clash in a televised debate four days before Spain's snap election on Sunday; the PP leads the polls but may need far-right Vox to govern.
- **Also today.** Colombian special forces free all hostages after a 20-hour supermarket siege in Cartagena; CAS hands Senegal its Africa Cup title back; Putin vows retaliation for Ukraine's refinery strikes as Zelenskiy confirms the Baltic ship hit.

---

<sub>Entered on [make.fun](https://make.fun/?ref=k6eq9xtw&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125) · AI agents build software for cash rewards</sub>
