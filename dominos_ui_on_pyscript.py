#!/usr/bin/env -S uv run --script

"""
Running this script opens a PyScript-based graphical user interface for
playing racehorse dominos in the local web browser.

The game board looks similar to images/tkDomino.py.png but uses PyScript
instead of tkinter.  Dominos are SVG images consistent with dominos_svg.py.
Each player is dealt 7 random dominos shown in boxes at the top and bottom.
The remaining dominos are placed face-down in the boneyard on the left.
The first player can drag a domino from their hand into the play area.
"""

# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "beautifulsoup4",
#     "httpx",
#     "pydantic",
# ]
# ///

import random
import sys
import tempfile
import webbrowser
from pathlib import Path

import httpx
from bs4 import BeautifulSoup, Tag
from pydantic import BaseModel

PYSCRIPT_VERSION = "2026.3.1"
PYSCRIPT_JS_URL = f"https://pyscript.net/releases/{PYSCRIPT_VERSION}/core.js"
PYSCRIPT_CSS_URL = f"https://pyscript.net/releases/{PYSCRIPT_VERSION}/core.css"

# Pip locations consistent with dominos_svg.py (0-6 pips)
PIP_OFFSETS = (0.25, 0.5, 0.75)
PIP_LOCATIONS: tuple[tuple[tuple[int, int], ...], ...] = (
    (),
    ((1, 1),),
    ((0, 0), (2, 2)),
    ((0, 0), (1, 1), (2, 2)),
    ((0, 0), (0, 2), (2, 0), (2, 2)),
    ((0, 0), (0, 2), (1, 1), (2, 0), (2, 2)),
    ((0, 0), (0, 1), (0, 2), (2, 0), (2, 1), (2, 2)),
)


class GameState(BaseModel):
    """Pydantic model capturing a complete racehorse dominos game state."""

    player0_hand: list[list[int]]  # human player (shown at bottom)
    player1_hand: list[list[int]]  # computer player (shown at top)
    boneyard: list[list[int]]  # bones not yet dealt, shown face-down
    play_chain: list[list[int]] = []
    scores: list[int] = [0, 0]
    current_player: int = 0
    message: str = "Your turn: drag a domino from your hand to the play area."


def all_domino_bones() -> list[list[int]]:
    """Return all 28 unique domino bones as [low, high] pairs."""
    return [[i, j] for i in range(7) for j in range(i, 7)]


def deal_game() -> GameState:
    """Shuffle all 28 bones and deal 7 each; the rest go to the boneyard."""
    bones = all_domino_bones()
    random.shuffle(bones)
    return GameState(
        player0_hand=bones[:7],
        player1_hand=bones[7:14],
        boneyard=bones[14:],
    )


def _half_svg(pip: int, half: int, pad: int, w: int) -> str:
    """Return SVG elements for one half of a domino (one die face)."""
    y0 = pad + half * w
    parts: list[str] = [
        f'<rect x="{pad}" y="{y0}" width="{w}" height="{w}" fill="white" stroke="blue" stroke-width="1"/>'
    ]
    r = max(2.0, w * 0.055)
    for xi, yi in PIP_LOCATIONS[pip]:
        cx = pad + PIP_OFFSETS[xi] * w
        cy = y0 + PIP_OFFSETS[yi] * w
        parts.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="blue"/>')
    return "".join(parts)


def make_domino_svg(top: int, bottom: int, *, w: int = 55, face_down: bool = False) -> str:
    """Generate an inline SVG string for one domino bone.

    Args:
        top: pip count for the top half (0-6).
        bottom: pip count for the bottom half (0-6).
        w: width of each half in pixels; the full bone is w x (2*w).
        face_down: when True the bone is rendered as a plain grey rectangle.
    """
    h, pad = w * 2, 3
    tw, th = w + 2 * pad, h + 2 * pad
    rx = w // 10

    if face_down:
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{tw}" height="{th}">'
            f'<rect x="{pad}" y="{pad}" width="{w}" height="{h}" rx="{rx}" '
            f'fill="#666" stroke="#444" stroke-width="1.5"/>'
            f"</svg>"
        )

    dy = pad + w
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{tw}" height="{th}">'
        f"{_half_svg(top, 0, pad, w)}"
        f"{_half_svg(bottom, 1, pad, w)}"
        f'<line x1="{pad}" y1="{dy}" x2="{pad + w}" y2="{dy}" '
        f'stroke="blue" stroke-width="1.5"/>'
        f"</svg>"
    )


# ---------------------------------------------------------------------------
# Python code that runs inside the browser via PyScript
# ---------------------------------------------------------------------------
_PYSCRIPT_CODE = """\
import json
import random

from pyscript import document, ffi, window

# ---------------------------------------------------------------------------
# Game constants
# ---------------------------------------------------------------------------
_SPINNER_MULTIPLIER = 2   # doubles score both open ends of a spinner
_SCORING_DIVISOR = 5      # racehorse: score a point for every 5 pips
_WIN_SCORE = 30           # first player to reach this score wins the match
_BONEYARD_MIN = 2         # must leave at least this many bones in boneyard

# ---------------------------------------------------------------------------
# Pip data (mirrors the host-side PIP_OFFSETS / PIP_LOCATIONS)
# ---------------------------------------------------------------------------
_PIP_OFFSETS = (0.25, 0.5, 0.75)
_PIP_LOCATIONS = (
    (),
    ((1, 1),),
    ((0, 0), (2, 2)),
    ((0, 0), (1, 1), (2, 2)),
    ((0, 0), (0, 2), (2, 0), (2, 2)),
    ((0, 0), (0, 2), (1, 1), (2, 0), (2, 2)),
    ((0, 0), (0, 1), (0, 2), (2, 0), (2, 1), (2, 2)),
)


def _half_svg(pip, half, pad, w):
    y0 = pad + half * w
    r = max(2.0, w * 0.055)
    parts = [
        f'<rect x="{pad}" y="{y0}" width="{w}" height="{w}" '
        f'fill="white" stroke="blue" stroke-width="1"/>'
    ]
    for xi, yi in _PIP_LOCATIONS[pip]:
        cx = pad + _PIP_OFFSETS[xi] * w
        cy = y0 + _PIP_OFFSETS[yi] * w
        parts.append(
            f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="blue"/>'
        )
    return "".join(parts)


def _half_svg_h(pip, half, pad, w):
    x0 = pad + half * w
    r = max(2.0, w * 0.055)
    parts = [
        f'<rect x="{x0}" y="{pad}" width="{w}" height="{w}" '
        f'fill="white" stroke="blue" stroke-width="1"/>'
    ]
    for xi, yi in _PIP_LOCATIONS[pip]:
        cx = x0 + _PIP_OFFSETS[xi] * w
        cy = pad + _PIP_OFFSETS[yi] * w
        parts.append(
            f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="blue"/>'
        )
    return "".join(parts)


def _domino_svg_h(top, bottom, w=55, face_down=False):
    h, pad = w * 2, 3
    tw, th = h + 2 * pad, w + 2 * pad
    rx = w // 10
    if face_down:
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{tw}" height="{th}">'
            f'<rect x="{pad}" y="{pad}" width="{h}" height="{w}" rx="{rx}" '
            f'fill="#666" stroke="#444" stroke-width="1.5"/></svg>'
        )
    dx = pad + w
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{tw}" height="{th}">'
        f"{_half_svg_h(top, 0, pad, w)}"
        f"{_half_svg_h(bottom, 1, pad, w)}"
        f'<line x1="{dx}" y1="{pad}" x2="{dx}" y2="{pad + w}" '
        f'stroke="blue" stroke-width="1.5"/></svg>'
    )


def _domino_svg(top, bottom, w=55, face_down=False):
    h, pad = w * 2, 3
    tw, th = w + 2 * pad, h + 2 * pad
    rx = w // 10
    if face_down:
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{tw}" height="{th}">'
            f'<rect x="{pad}" y="{pad}" width="{w}" height="{h}" rx="{rx}" '
            f'fill="#666" stroke="#444" stroke-width="1.5"/></svg>'
        )
    dy = pad + w
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{tw}" height="{th}">'
        f"{_half_svg(top, 0, pad, w)}"
        f"{_half_svg(bottom, 1, pad, w)}"
        f'<line x1="{pad}" y1="{dy}" x2="{pad + w}" y2="{dy}" '
        f'stroke="blue" stroke-width="1.5"/></svg>'
    )


# ---------------------------------------------------------------------------
# Game state (mutable; starts from the JSON embedded by the host script)
# ---------------------------------------------------------------------------
_raw = json.loads(document.getElementById("game-state-data").textContent)
_hand0 = [list(t) for t in _raw["player0_hand"]]   # human hand
_hand1 = [list(t) for t in _raw["player1_hand"]]   # computer hand
_boneyard = [list(t) for t in _raw["boneyard"]]
_chain: list[list[int]] = []   # played dominos, in chain order
_left_end: int | None = None   # open left end of the chain
_right_end: int | None = None  # open right end of the chain
_scores = [0, 0]
_current_player = 0            # 0 = human, 1 = computer
_needs_boneyard_draw = False   # True when human must draw from boneyard
_game_over = False             # True when the match has been won
_consecutive_passes = 0        # tracks back-to-back passes; game stuck when >= 2


# ---------------------------------------------------------------------------
# Rendering helpers
# ---------------------------------------------------------------------------
def _make_bone_div(top, bottom, draggable=False, face_down=False,
                   horizontal=False, from_boneyard=False):
    div = document.createElement("div")
    div.className = "domino-bone"
    div.setAttribute("data-top", str(top))
    div.setAttribute("data-bottom", str(bottom))
    if from_boneyard:
        div.setAttribute("data-from-boneyard", "true")
    div.setAttribute("draggable", "true" if draggable else "false")
    if horizontal:
        div.innerHTML = _domino_svg_h(top, bottom, face_down=face_down)
    else:
        div.innerHTML = _domino_svg(top, bottom, face_down=face_down)
    return div


def _render_hand(hand, area_id, draggable=False, face_down=False, horizontal=False):
    area = document.getElementById(area_id)
    area.innerHTML = ""
    for bone in hand:
        bone_div = _make_bone_div(bone[0], bone[1], draggable=draggable,
                                  face_down=face_down, horizontal=horizontal)
        area.appendChild(bone_div)
    if draggable:
        for el in area.querySelectorAll(".domino-bone[draggable='true']"):
            el.addEventListener("dragstart", ffi.create_proxy(_on_dragstart))


def _render_boneyard(draggable_to_hand=False):
    area = document.getElementById("boneyard-area")
    area.innerHTML = ""
    lbl = document.createElement("div")
    lbl.className = "area-label"
    lbl.textContent = f"Boneyard ({len(_boneyard)})"
    area.appendChild(lbl)
    for bone in _boneyard:
        bone_div = _make_bone_div(
            bone[0], bone[1],
            draggable=draggable_to_hand,
            face_down=not draggable_to_hand,
            horizontal=True,
            from_boneyard=True,
        )
        area.appendChild(bone_div)
    if draggable_to_hand:
        for el in area.querySelectorAll(".domino-bone[draggable='true']"):
            el.addEventListener("dragstart", ffi.create_proxy(_on_dragstart_boneyard))
    area.className = "draw-mode" if draggable_to_hand else ""


def _render_play_area():
    area = document.getElementById("play-area")
    area.innerHTML = ""
    for bone in _chain:
        is_double = bone[0] == bone[1]
        div = _make_bone_div(bone[0], bone[1], horizontal=not is_double)
        area.appendChild(div)


def _render_scores():
    document.getElementById("score-p0").textContent = str(_scores[0])
    document.getElementById("score-p1").textContent = str(_scores[1])


def _set_message(msg):
    document.getElementById("status-msg").textContent = msg


def _render_all():
    is_human_turn = _current_player == 0 and not _game_over
    _render_hand(_hand0, "player0-hand",
                 draggable=is_human_turn and not _needs_boneyard_draw)
    _render_hand(_hand1, "player1-hand", face_down=True)
    _render_boneyard(draggable_to_hand=_needs_boneyard_draw)
    _render_play_area()
    _render_scores()
    play_area = document.getElementById("play-area")
    if _needs_boneyard_draw or not is_human_turn:
        play_area.style.pointerEvents = "none"
        play_area.style.opacity = "0.5"
    else:
        play_area.style.pointerEvents = "auto"
        play_area.style.opacity = "1"


# ---------------------------------------------------------------------------
# Game logic helpers
# ---------------------------------------------------------------------------
def _is_double(bone):
    return bone[0] == bone[1]


def _hand_value(hand):
    return sum(t[0] + t[1] for t in hand)


def _score_chain():
    if not _chain:
        return 0
    if len(_chain) == 1 and _chain[0][0] == _chain[0][1]:
        total = _chain[0][0] * _SPINNER_MULTIPLIER   # spinner: count both ends
    else:
        total = (_left_end or 0) + (_right_end or 0)
    return total if total % _SCORING_DIVISOR == 0 else 0


def _simulate_chain_score_after_play(bone):
    # Return the chain sum that would result from playing bone (0 if not scoring).
    a, b = bone[0], bone[1]
    if not _chain:
        total = a * 2 if a == b else a + b
    elif a == _left_end:
        total = (b or 0) + (_right_end or 0)
    elif b == _left_end:
        total = (a or 0) + (_right_end or 0)
    elif a == _right_end:
        total = (_left_end or 0) + (b or 0)
    elif b == _right_end:
        total = (_left_end or 0) + (a or 0)
    else:
        return 0
    return total if total % _SCORING_DIVISOR == 0 else 0


def _find_bone(hand, top, bottom):
    for bone in hand:
        if bone == [top, bottom] or bone == [bottom, top]:
            return bone
    return None


def _apply_play(top, bottom, hand):
    global _left_end, _right_end
    bone = _find_bone(hand, top, bottom)
    if bone is None:
        return False
    hand.remove(bone)
    if not _chain:
        _chain.append([top, bottom])
        _left_end = top
        _right_end = bottom
    elif top == _left_end:
        _chain.insert(0, [bottom, top])
        _left_end = bottom
    elif bottom == _left_end:
        _chain.insert(0, [top, bottom])
        _left_end = top
    elif top == _right_end:
        _chain.append([top, bottom])
        _right_end = bottom
    elif bottom == _right_end:
        _chain.append([bottom, top])
        _right_end = top
    else:
        hand.append(bone)  # put it back - invalid placement
        return False
    return True


def _can_play(top, bottom):
    if not _chain:
        return True
    return top in (_left_end, _right_end) or bottom in (_left_end, _right_end)


def _valid_plays(hand):
    return [t for t in hand if _can_play(t[0], t[1])]


# ---------------------------------------------------------------------------
# Win / end-of-hand logic
# ---------------------------------------------------------------------------
def _show_new_game_button():
    btn = document.getElementById("new-game-btn")
    if btn:
        btn.style.display = "inline-block"


def _check_win_after_play(player_idx):
    # Player emptied their hand: award bonus pts and check for match win.
    global _game_over
    opp_hand = _hand1 if player_idx == 0 else _hand0
    bonus = _hand_value(opp_hand) // _SCORING_DIVISOR
    _scores[player_idx] += bonus
    _render_scores()
    winner_name = "You" if player_idx == 0 else "Computer"
    if _scores[player_idx] >= _WIN_SCORE:
        _game_over = True
        _render_all()
        _set_message(
            f"{winner_name} wins the match with {_scores[player_idx]} points! "
            f"(+{bonus} pts from opponent's hand)"
        )
        _show_new_game_button()
    else:
        _render_all()
        _set_message(
            f"{winner_name} cleared the hand! +{bonus} bonus pts. "
            f"Scores: You {_scores[0]}, CPU {_scores[1]}. Dealing new hand..."
        )
        _deal_new_hand()


def _deal_new_hand():
    # Shuffle and deal a fresh set of bones, preserving match scores.
    global _hand0, _hand1, _boneyard, _chain, _left_end, _right_end
    global _current_player, _needs_boneyard_draw, _consecutive_passes
    bones = [[i, j] for i in range(7) for j in range(i, 7)]
    random.shuffle(bones)
    _hand0 = [list(t) for t in bones[:7]]
    _hand1 = [list(t) for t in bones[7:14]]
    _boneyard = [list(t) for t in bones[14:]]
    _chain.clear()
    _left_end = None
    _right_end = None
    _current_player = 0
    _needs_boneyard_draw = False
    _consecutive_passes = 0
    _render_all()
    _set_message("New hand dealt! Your turn: drag a domino to the play area.")


def _end_stuck_game():
    # Called when both players pass in a row - award points to the player with fewer pips.
    global _game_over
    v0 = _hand_value(_hand0)
    v1 = _hand_value(_hand1)
    if v0 < v1:
        winner_idx, bonus = 0, v1 // _SCORING_DIVISOR
    elif v1 < v0:
        winner_idx, bonus = 1, v0 // _SCORING_DIVISOR
    else:
        _game_over = True
        _render_all()
        _set_message("Game stuck - both hands equal. No winner this hand.")
        _show_new_game_button()
        return
    _scores[winner_idx] += bonus
    _render_scores()
    winner_name = "You" if winner_idx == 0 else "Computer"
    if _scores[winner_idx] >= _WIN_SCORE:
        _game_over = True
        _render_all()
        _set_message(f"Game stuck! {winner_name} wins the match with {_scores[winner_idx]} pts!")
        _show_new_game_button()
    else:
        _render_all()
        _set_message(
            f"Game stuck! {winner_name} had fewer pips, gains {bonus} pts. "
            f"Scores: You {_scores[0]}, CPU {_scores[1]}. Dealing new hand..."
        )
        _deal_new_hand()


# ---------------------------------------------------------------------------
# Turn management: start_turn handles boneyard draws and switches players
# ---------------------------------------------------------------------------
def _start_turn(player_idx, prefix=""):
    # Begin a turn for player_idx, drawing from boneyard if necessary.
    global _current_player, _needs_boneyard_draw, _consecutive_passes
    _current_player = player_idx
    _needs_boneyard_draw = False
    hand = _hand0 if player_idx == 0 else _hand1
    if _valid_plays(hand):
        _render_all()
        if player_idx == 1:
            _set_message(prefix + "Computer's turn...")
            _computer_play()
        else:
            _set_message(prefix + "Your turn: drag a domino to the play area.")
    elif len(_boneyard) > _BONEYARD_MIN:
        if player_idx == 1:
            _render_all()
            _set_message(prefix + "Computer draws from boneyard...")
            _computer_draw_and_play()
        else:
            _needs_boneyard_draw = True
            _render_all()
            _set_message(prefix + "No playable bones! Drag a bone from the Boneyard to your hand.")
    else:
        _consecutive_passes += 1
        if _consecutive_passes >= 2:
            _end_stuck_game()
        else:
            other = 1 - player_idx
            _render_all()
            _set_message(
                prefix +
                f"{'You' if player_idx == 0 else 'Computer'} passes "
                f"(no valid bones, boneyard too small). "
                f"{'Computer' if player_idx == 0 else 'Your'} turn."
            )
            _start_turn(other)


def _after_play(player_idx, bone_played):
    # Called after player successfully places a bone; handles scoring, go-again, and win.
    global _consecutive_passes
    _consecutive_passes = 0
    hand = _hand0 if player_idx == 0 else _hand1
    if not hand:
        _check_win_after_play(player_idx)
        return
    pts = _score_chain()
    scored = pts > 0
    is_dbl = _is_double(bone_played)
    if scored:
        _scores[player_idx] += pts // _SCORING_DIVISOR
    if scored or is_dbl:
        if is_dbl and scored:
            prefix = (
                f"{'You' if player_idx == 0 else 'Computer'} played a double "
                f"and scored {pts // _SCORING_DIVISOR} pt(s)! Go again. "
            )
        elif is_dbl:
            prefix = f"{'You' if player_idx == 0 else 'Computer'} played a double! Go again. "
        else:
            prefix = (
                f"{'You' if player_idx == 0 else 'Computer'} scored "
                f"{pts // _SCORING_DIVISOR} pt(s)! Go again. "
            )
        _start_turn(player_idx, prefix=prefix)
    else:
        _start_turn(1 - player_idx)


# ---------------------------------------------------------------------------
# Computer player
# ---------------------------------------------------------------------------
def _computer_draw_and_play():
    # Computer draws from boneyard until it can play (or boneyard gets too small).
    drawn_count = 0
    while not _valid_plays(_hand1) and len(_boneyard) > _BONEYARD_MIN:
        drawn = _boneyard.pop(random.randrange(len(_boneyard)))
        _hand1.append(drawn)
        drawn_count += 1
    _render_all()
    if drawn_count:
        draw_msg = f"Computer drew {drawn_count} bone(s) from the boneyard. "
    else:
        draw_msg = ""
    if _valid_plays(_hand1):
        _set_message(draw_msg + "Computer's turn...")
        _computer_play()
    else:
        global _consecutive_passes
        _consecutive_passes += 1
        if _consecutive_passes >= 2:
            _end_stuck_game()
        else:
            _set_message(draw_msg + "Computer passes - no valid bones. Your turn.")
            _start_turn(0)


def _computer_play():
    # Computer picks the best available bone and plays it.
    plays = _valid_plays(_hand1)
    if not plays:
        return
    # Rank plays: prefer (1) scoring plays by pts, (2) doubles for go-again,
    # (3) highest pip total to shed high-value bones from hand.
    best = max(
        plays,
        key=lambda t: (
            _simulate_chain_score_after_play(t),
            _is_double(t),
            t[0] + t[1],
        ),
    )
    if _apply_play(best[0], best[1], _hand1):
        _set_message(f"Computer played [{best[0]}|{best[1]}].")
        _after_play(1, best)
    else:
        _set_message("Computer could not play - passing.")
        _start_turn(0)


# ---------------------------------------------------------------------------
# Drag-and-drop handlers
# ---------------------------------------------------------------------------
def _on_dragstart(event):
    top = event.target.getAttribute("data-top")
    bottom = event.target.getAttribute("data-bottom")
    event.dataTransfer.setData("text/plain", f"{top},{bottom}")
    event.dataTransfer.effectAllowed = "move"


def _on_dragstart_boneyard(event):
    top = event.target.getAttribute("data-top")
    bottom = event.target.getAttribute("data-bottom")
    event.dataTransfer.setData("text/plain", f"boneyard:{top},{bottom}")
    event.dataTransfer.effectAllowed = "move"


def _on_dragover(event):
    event.preventDefault()
    event.dataTransfer.dropEffect = "move"


def _on_drop(event):
    event.preventDefault()
    if _current_player != 0 or _needs_boneyard_draw or _game_over:
        return
    data = event.dataTransfer.getData("text/plain")
    if data.startswith("boneyard:"):
        return  # boneyard bones go to hand, not play area
    top_s, bottom_s = data.split(",")
    top, bottom = int(top_s), int(bottom_s)
    if not _can_play(top, bottom):
        _set_message(f"[{top}|{bottom}] cannot be played here - try another bone.")
        return
    if _apply_play(top, bottom, _hand0):
        _after_play(0, [top, bottom])
    else:
        _set_message("That move is not valid.")


def _on_drop_boneyard_to_hand(event):
    # Boneyard bone dropped onto the human's hand area.
    global _needs_boneyard_draw, _consecutive_passes
    event.preventDefault()
    if not _needs_boneyard_draw or _game_over:
        return
    data = event.dataTransfer.getData("text/plain")
    if not data.startswith("boneyard:"):
        return
    _, coords = data.split(":", 1)
    top_s, bottom_s = coords.split(",")
    top, bottom = int(top_s), int(bottom_s)
    bone = _find_bone(_boneyard, top, bottom)
    if bone is None:
        return
    _boneyard.remove(bone)
    _hand0.append(bone)
    if _valid_plays(_hand0) or len(_boneyard) <= _BONEYARD_MIN:
        _needs_boneyard_draw = False
        if _valid_plays(_hand0):
            _render_all()
            _set_message(f"Drew [{top}|{bottom}]. Your turn: drag a domino to the play area.")
        else:
            _consecutive_passes += 1
            if _consecutive_passes >= 2:
                _end_stuck_game()
            else:
                _render_all()
                _set_message(
                    f"Drew [{top}|{bottom}] but still no playable bones. Computer's turn."
                )
                _start_turn(1)
    else:
        _render_all()
        _set_message(
            f"Drew [{top}|{bottom}]. Still no playable bones - draw another from the Boneyard."
        )


def _on_new_game(event):  # noqa: ARG001
    window.location.reload()


# ---------------------------------------------------------------------------
# Bootstrap
# ---------------------------------------------------------------------------
_play_area = document.getElementById("play-area")
_play_area.addEventListener("dragover", ffi.create_proxy(_on_dragover))
_play_area.addEventListener("drop", ffi.create_proxy(_on_drop))

_hand0_area = document.getElementById("player0-hand")
_hand0_area.addEventListener("dragover", ffi.create_proxy(_on_dragover))
_hand0_area.addEventListener("drop", ffi.create_proxy(_on_drop_boneyard_to_hand))

_new_game_btn = document.getElementById("new-game-btn")
if _new_game_btn:
    _new_game_btn.addEventListener("click", ffi.create_proxy(_on_new_game))

_render_all()
_set_message(_raw["message"])
"""


# ---------------------------------------------------------------------------
# CSS for the game board
# ---------------------------------------------------------------------------
_CSS = """\
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
    font-family: sans-serif;
    background: #2d5a1b;
    color: #fff;
    height: 100vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 8px;
    gap: 6px;
}
h1 { font-size: 1.1rem; letter-spacing: 2px; }
#board {
    display: grid;
    grid-template-columns: 130px 1fr 90px;
    grid-template-rows: auto 1fr auto;
    gap: 6px;
    width: 100%;
    max-width: 900px;
    flex: 1;
}
.player-hand {
    grid-column: 1 / -1;
    display: flex;
    flex-wrap: wrap;
    gap: 4px;
    background: rgba(0,0,0,.3);
    border-radius: 8px;
    padding: 6px;
    min-height: 70px;
    align-items: center;
    justify-content: space-evenly;
}
#boneyard-area {
    display: flex;
    flex-direction: column;
    gap: 3px;
    background: rgba(0,0,0,.4);
    border-radius: 8px;
    padding: 6px;
    align-items: center;
    overflow-y: auto;
}
#play-area {
    background: rgba(255,255,255,.08);
    border: 2px dashed rgba(255,255,255,.4);
    border-radius: 8px;
    display: flex;
    flex-direction: row;
    flex-wrap: nowrap;
    gap: 4px;
    padding: 8px;
    align-items: center;
    overflow-x: auto;
}
#scoreboard {
    display: flex;
    flex-direction: column;
    gap: 8px;
    background: rgba(0,0,0,.4);
    border-radius: 8px;
    padding: 8px;
    font-size: 0.85rem;
    align-items: center;
}
#scoreboard h2 { font-size: 0.9rem; }
.score-row { display: flex; flex-direction: column; align-items: center; gap: 2px; }
.score-val { font-size: 1.4rem; font-weight: bold; color: #ffd700; }
#status-bar {
    width: 100%;
    max-width: 900px;
    background: rgba(0,0,0,.4);
    border-radius: 6px;
    padding: 6px 10px;
    font-size: 0.9rem;
    text-align: center;
}
.domino-bone {
    cursor: grab;
    border-radius: 4px;
    transition: transform .1s;
}
.domino-bone:hover { transform: scale(1.08); }
.area-label {
    font-size: 0.7rem;
    opacity: .7;
    text-align: center;
    margin-bottom: 2px;
}
#boneyard-area.draw-mode {
    border: 2px solid #ffd700;
    background: rgba(255, 215, 0, .15);
}
#boneyard-area.draw-mode .domino-bone {
    cursor: grab;
    outline: 2px solid #ffd700;
    border-radius: 4px;
}
#player0-hand.drop-target {
    outline: 2px dashed #ffd700;
}
#new-game-btn {
    display: none;
    margin-left: 10px;
    padding: 6px 18px;
    background: #ffd700;
    color: #000;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 0.9rem;
    font-weight: bold;
}
#new-game-btn:hover { background: #ffe84d; }
"""


def _check_pyscript_cdn() -> None:
    """Warn if the PyScript CDN appears unreachable (requires internet)."""
    try:
        r = httpx.head(PYSCRIPT_CSS_URL, timeout=5.0, follow_redirects=True)
        if r.status_code >= 400:
            print(
                f"Warning: PyScript CDN returned {r.status_code}. "
                "The page may not load without internet access.",
                file=sys.stderr,
            )
    except httpx.RequestError:
        print(
            "Warning: Could not reach PyScript CDN. The page requires an internet connection to load.",
            file=sys.stderr,
        )


def _add_tag(soup: BeautifulSoup, parent: Tag, tag_name: str, **attrs: str) -> Tag:
    """Create and append a new tag to parent, returning the tag."""
    tag = soup.new_tag(tag_name, attrs=attrs)
    parent.append(tag)
    return tag


def _build_head(soup: BeautifulSoup, html_tag: Tag) -> None:
    """Populate the <head> element of the game page."""
    head = _add_tag(soup, html_tag, "head")
    _add_tag(soup, head, "meta", charset="UTF-8")
    _add_tag(
        soup,
        head,
        "meta",
        name="viewport",
        content="width=device-width, initial-scale=1.0",
    )
    title = soup.new_tag("title")
    title.string = "Claussoft Dominos - Racehorse"
    head.append(title)
    _add_tag(soup, head, "link", rel="stylesheet", href=PYSCRIPT_CSS_URL)
    style = soup.new_tag("style")
    style.string = _CSS
    head.append(style)


def _build_board(soup: BeautifulSoup, body: Tag) -> None:
    """Add the game board grid (player hands, boneyard, play area, scoreboard)."""
    board = _add_tag(soup, body, "div", id="board")

    # Player 1 hand (top - computer)
    p1_div = _add_tag(soup, board, "div", id="player1-hand")
    p1_div["class"] = "player-hand"
    lbl1 = soup.new_tag("div")
    lbl1["class"] = "area-label"
    lbl1.string = "Computer's hand"
    p1_div.append(lbl1)

    # Boneyard (left column)
    by_div = _add_tag(soup, board, "div", id="boneyard-area")
    lbl_by = soup.new_tag("div")
    lbl_by["class"] = "area-label"
    lbl_by.string = "Boneyard"
    by_div.append(lbl_by)

    # Play area (centre)
    _add_tag(soup, board, "div", id="play-area")

    # Scoreboard (right column)
    sb = _add_tag(soup, board, "div", id="scoreboard")
    h2 = soup.new_tag("h2")
    h2.string = "Score"
    sb.append(h2)
    for player, label in ((0, "You"), (1, "CPU")):
        row = soup.new_tag("div")
        row["class"] = "score-row"
        lbl = soup.new_tag("span")
        lbl.string = label
        val = soup.new_tag("span")
        val["class"] = "score-val"
        val["id"] = f"score-p{player}"
        val.string = "0"
        row.append(lbl)
        row.append(val)
        sb.append(row)

    # Player 0 hand (bottom - human)
    p0_div = _add_tag(soup, board, "div", id="player0-hand")
    p0_div["class"] = "player-hand"
    lbl0 = soup.new_tag("div")
    lbl0["class"] = "area-label"
    lbl0.string = "Your hand (drag a bone to the play area)"
    p0_div.append(lbl0)


def build_html(state: GameState) -> str:
    """Build the complete HTML page as a string using BeautifulSoup."""
    soup = BeautifulSoup("<!DOCTYPE html><html lang='en'></html>", "html.parser")
    html_tag = soup.find("html")

    _build_head(soup, html_tag)

    body = _add_tag(soup, html_tag, "body")
    h1 = soup.new_tag("h1")
    h1.string = "Claussoft Dominos - Racehorse"
    body.append(h1)

    _build_board(soup, body)

    # Status bar
    status = _add_tag(soup, body, "div", id="status-bar")
    msg_span = soup.new_tag("span")
    msg_span["id"] = "status-msg"
    msg_span.string = state.message
    status.append(msg_span)
    new_game_btn = soup.new_tag("button")
    new_game_btn["id"] = "new-game-btn"
    new_game_btn.string = "New Game"
    status.append(new_game_btn)

    # Embedded game-state JSON (hidden)
    data_script = soup.new_tag("script")
    data_script["id"] = "game-state-data"
    data_script["type"] = "application/json"
    data_script.string = state.model_dump_json()
    body.append(data_script)

    # PyScript runtime
    _add_tag(soup, body, "script", type="module", src=PYSCRIPT_JS_URL)

    # Embedded Python game logic
    py_script = soup.new_tag("script", type="py")
    py_script.string = _PYSCRIPT_CODE
    body.append(py_script)

    return str(soup)


def main() -> None:
    """Generate the game HTML and open it in the default web browser."""
    _check_pyscript_cdn()
    state = deal_game()
    html = build_html(state)
    with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False, encoding="utf-8") as fh:
        fh.write(html)
        html_path = Path(fh.name)
    print(f"Opening {html_path}")
    webbrowser.open(html_path.as_uri())


if __name__ == "__main__":
    main()
