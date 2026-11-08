#!/usr/bin/env python3
"""Analyze my chess.com games with Stockfish. Usage: analyze.py games.json [more.json ...] > report.json"""
import io, json, re, sys, collections
import chess, chess.pgn, chess.engine

ME = "your_username"  # chess.com username
SF = "stockfish"  # path to the Stockfish binary
LIMIT = chess.engine.Limit(time=0.08)


def cp(score, pov):
    return score.pov(pov).score(mate_score=10000)


def winp(c):  # lichess-style win probability from centipawns
    import math
    return 50 + 50 * (2 / (1 + math.exp(-0.00368208 * c)) - 1)


def clk(node):
    m = re.search(r"\[%clk (\d+):(\d+):(\d+(?:\.\d+)?)\]", node.comment or "")
    return int(m[1]) * 3600 + int(m[2]) * 60 + float(m[3]) if m else None


def main():
    games = []
    for f in sys.argv[1:]:
        games += json.load(open(f)).get("games", [])
    eng = chess.engine.SimpleEngine.popen_uci(SF)
    eng.configure({"Threads": 3, "Hash": 256})
    out = []
    for g in games:
        if g.get("rules") != "chess" or g["time_class"] not in ("rapid", "daily", "blitz"):
            continue
        pg = chess.pgn.read_game(io.StringIO(g["pgn"]))
        color = chess.WHITE if g["white"]["username"].lower() == ME else chess.BLACK
        mycol = "white" if color else "black"
        res = g[mycol]["result"]
        board = pg.board()
        info = eng.analyse(board, LIMIT)
        prev = cp(info["score"], color)
        moves = []
        node = pg
        for nxt in pg.mainline():
            mv = nxt.move
            mine = board.turn == color
            best = info.get("pv", [None])[0]
            san = board.san(mv)
            fen = board.fen()
            capt = board.is_capture(mv)
            board.push(mv)
            info = eng.analyse(board, LIMIT)
            now = cp(info["score"], color)
            if mine:
                loss = winp(prev) - winp(now)
                reply = info.get("pv", [None])[0]
                moves.append({
                    "ply": board.ply(), "san": san, "best": chess.Board(fen).san(best) if best else None,
                    "cp_before": prev, "cp_after": now, "wp_loss": round(loss, 1), "fen": fen,
                    "clock": clk(nxt), "opp_reply_capture": bool(reply and board.is_capture(reply)),
                    "pieces": len(board.piece_map()),
                })
            prev = now
        out.append({"url": g["url"], "tc": g["time_class"], "time_control": g["time_control"], "color": mycol,
                    "result": res, "opp_result": g["black" if color else "white"]["result"],
                    "opp_rating": g["black" if color else "white"]["rating"], "my_rating": g[mycol]["rating"],
                    "eco": (re.search(r'openings/([^"]+)"', g["pgn"]) or [None, "?"])[1], "moves": moves})
    eng.quit()
    json.dump(out, sys.stdout)


if __name__ == "__main__":
    main()
