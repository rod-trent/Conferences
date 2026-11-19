# Demo 06 — Build vs. Buy: the Three-Year View

Slide 31 · runs offline, standard library only · also on the [demo site](https://eldk2027-demos.vercel.app/?demo=tco)

A transparent three-year cost model: run your own multi-agent SOC, or run Microsoft Perception and build only what it doesn't cover.

## Facts vs. assumptions

`assumptions.json` keeps the two apart.

**Facts** (Microsoft, checked 19 Nov 2026):

- $6 per overage SCU.
- E5/E7 include 400 SCUs a month per 1,000 user licences, capped at 10,000.
- Two platform retirements on 31 March 2027.
- Perception is consumption-priced, with **no public rate card**.

**Assumptions:** engineering weeks, the cost of an engineer-week, maintenance load, SCU use. Replace them with your own.

Because there's no rate card, the model doesn't invent a Perception price. It computes the **break-even**: the monthly Perception spend below which buying is cheaper. Compare that with the figure from Microsoft's cost calculator, or pass your quote with `--quote`.

## Run it

```bash
cd demos/06-build-vs-buy
python build_vs_buy.py                    # mid-size SOC
python build_vs_buy.py --profile small
python build_vs_buy.py --profile large
python build_vs_buy.py --quote 12000      # with a (hypothetical) monthly quote
python build_vs_buy.py --sensitivity      # which assumption moves the answer most
python build_vs_buy.py --self-test        # 10 checks
```
