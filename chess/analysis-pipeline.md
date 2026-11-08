# Chess game analysis pipeline

## Goal
Find *why* I lose rapid games, using data instead of gut feeling.

## How it works ([analyze.py](analyze.py))
1. Pull my games from the **chess.com public API** (`/pub/player/<user>/games/YYYY/MM`).
2. Replay each PGN with **python-chess**, then evaluate every position with **Stockfish 19** over UCI (0.08 s per position, 3 threads).
3. For each of my moves, compute the **win-probability drop**. Classify as inaccuracy (≥5%), mistake (≥10%) or blunder (≥20%), and record the phase, my clock, and whether the opponent's best reply is a capture (= I hung something).
4. Aggregate across games.

## Results (62 games, Aug–Nov 2026)
- Rapid: **2.3 blunders/game**. Daily (correspondence): **0.5**.
- Median clock at move 20: **~7 of 10 minutes left**. Only 7 of 115 rapid blunders came under one minute. **I'm moving too fast, not running out of time.**
- 39% of blunders hung material. My worst moves skipped forcing moves (one missed mate in 1).
- Puzzle rating 1653 vs rapid 817 confirms it: the tactics are there, the thinking process isn't.

## Skills used
Python, REST APIs, PGN parsing, UCI engine automation, data analysis.
