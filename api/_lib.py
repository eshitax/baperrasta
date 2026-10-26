import json
import math
import urllib.request
from datetime import datetime, timezone
from http import HTTPStatus


def week_id():
    now = datetime.now(timezone.utc).timestamp() * 1000
    t = math.floor((now + 21600000) / 86400000)
    start = (t - (t + 5) % 7) * 86400000
    return datetime.fromtimestamp(start / 1000, tz=timezone.utc).strftime("%Y-%m-%d")


def empty_board():
    return {"ok": True, "week": week_id(), "top": [], "all": [], "cut": 0}


def fetch_live_board():
    req = urllib.request.Request(
        "https://baperrasta.com/api/board",
        headers={"User-Agent": "BaperRastaClone/1.0", "Accept": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=6) as r:
            data = json.loads(r.read())
        if data.get("ok"):
            return data
    except Exception:
        pass
    return empty_board()


def rank_for(loss, rows):
    return 1 + sum(1 for row in rows if row.get("loss", 0) > loss)


def score_response(body):
    board = fetch_live_board()
    loss = int(body.get("loss") or 0)
    rows = board.get("top") or []
    cut = int(board.get("cut") or 0)
    week = board.get("week") or week_id()
    if loss <= cut:
        return {
            "ok": True, "week": week, "cut": cut, "best": loss,
            "rank": None, "need": cut + 50 - loss, "named": False,
        }
    return {
        "ok": True, "week": week, "cut": cut, "best": loss,
        "rank": rank_for(loss, rows), "need": 0, "named": False,
    }


def send(data, status=200):
    return {
        "statusCode": status,
        "headers": {
            "Content-Type": "application/json; charset=utf-8",
            "Cache-Control": "no-cache",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type",
        },
        "body": json.dumps(data, ensure_ascii=False),
    }
