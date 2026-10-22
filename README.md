# House Call

A top-down curling app for calling, analyzing and playing out shots, modeled on curling.gg.

- Place the broom to call the ice; the handle auto-sets when the broom crosses the center line.
- Set weight on a hog-to-hog dial; hold **Sweep** during a throw to carry a stone farther and straighter. Each team sweeps its own stones before the tee line; either team may sweep past it. The computer sweeps its own calls.
- **Suggest a shot** tests ~1,000 calls, checks the opponent's best reply, and rates each suggestion's difficulty with a one-line reason.
- **Review end** steps back through the end stone by stone, replays any throw exactly (sweeping included), and can play on from an earlier position.
- **Copy link** shares the position and your call; **Save image** saves a picture of the house.
- Play against the computer, a friend, or in practice mode, with free guard zone, hog line and hammer rules.

**Play it:** https://bgorichs.github.io/HouseCall/ (no sign-in needed)

Everything lives in a single file, `index.html`, with no build step. GitHub Pages serves it straight from `main`, and it also opens fine from disk. A copy also runs as a Claude artifact: https://claude.ai/artifact/2aEHPcKfdyfaA824tJbcRs

## Historic shots

**Historic shots** loads real positions from championship games. Call and throw the shot yourself, then compare it with the skip's actual call, the World Curling execution grade and the real result (which can be overlaid on the ice).

- Data: `data/*.pcn`, in [PCN](https://github.com/shinagaki/pcn) format (World Curling / CURLIT Shot by Shot, positions read from the published diagrams).
- `python3 tools/build_historic.py` regenerates the dataset embedded in `index.html`. To add a game, drop its `.pcn` file (with `@` board lines) in `data/`, add an entry with the positions to feature in `GAMES`, and re-run.
- Currently: PyeongChang 2018 women's bronze medal game (GBR–JPN), 10 positions.
