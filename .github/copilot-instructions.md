# Copilot Instructions for claussoft-dominos

## Development Tools

### uv
Use [uv](https://docs.astral.sh/uv/) as the Python package manager and project runner.

- Run scripts directly: `uv run script.py`
- Install dependencies: `uv add <package>`
- Run tools: `uv tool run ruff check .`

### PEP 723 – Inline Script Metadata
All standalone Python scripts should declare their dependencies and Python version
using [PEP 723](https://peps.python.org/pep-0723/) inline script metadata so they
can be run directly with `uv run`:

```python
#!/usr/bin/env -S uv run --script

# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "some-package",
# ]
# ///
```

### pre-commit
Use [pre-commit](https://pre-commit.com/) to enforce code quality before each commit.

- Install hooks: `pre-commit install`
- Run manually: `pre-commit run --all-files`
- Configuration lives in `.pre-commit-config.yaml`

When adding new linting or formatting hooks, add them to `.pre-commit-config.yaml`
rather than running tools ad-hoc.

### pytest
Use [pytest](https://docs.pytest.org/) for all tests.

- Run tests: `uv run pytest` or `python -m pytest`
- Tests live in the `tests/` directory
- New features and bug fixes should include tests in `tests/`
- Test files are named `test_*.py`

---

## Game Rules: Racehorse Dominoes

The PyScript UI (`dominos_ui_on_pyscript.py`) implements
[Racehorse Dominoes](http://www.dominorules.com/racehorse):

- Each player is initially dealt a hand of 7 dominoes.
- The remaining dominoes go face down in the boneyard.
- Dominoes can only be played against matching numbers.
- If no domino in a player's hand matches an open end, the player must draw
  from the boneyard until a playable domino is found or only 2 remain.
- If all open ends add up to a multiple of 5 the player scores `sum // 5` and
  goes again.
- If the player plays doubles they get to go again.  Doubles are played
  sideways (perpendicular to the line of play) and count 2× when scoring.
- The first double played becomes the **spinner**: once both horizontal ends
  have been played, vertical branches grow up and down from it.
- The player who clears their hand scores all pips in the opponent's hand
  divided by 5.  First to 30 points wins the match.

### Board layout
The played dominoes are **not** a simple chain (line).  After the spinner is
surrounded the board branches both horizontally **and** vertically, forming a
cross / plus shape:

```
          [top branch, outermost first]
                  ...
               [T|U]
                [spinner]
               [B|V]
                  ...
          [bottom branch]
[left end] ... [L|spinner] [spinner|R] ... [right end]
```

The `_played_dominoes` list holds only the horizontal run; `_top_branch` and
`_bottom_branch` hold the vertical arms.

---

## Spelling

The correct plural of "domino" is **dominoes** (with the letter "e").  All
identifiers, comments, strings, and documentation must use "dominoes".  The
legacy spelling "dominos" is incorrect and should not be introduced.

---

## Drawing Dominoes

### Face-up dominoes (human hand and play area)

Pre-made SVG images live in `images/dominoes_faceup/`.  Files are named
`domino_A_B.svg` where `A ≤ B` (e.g. `domino_3_4.svg`).  The file shows `A`
pips in the top half and `B` pips in the bottom half in portrait orientation.

- **Generated at startup**: `_load_domino_image_uris()` reads all 28 files
  and returns a `dict[str, str]` of base64-encoded SVG data URIs keyed by
  `"A_B"`.  These are embedded in the HTML at page-generation time and loaded
  from the DOM at PyScript startup into `_DOMINO_IMAGE_URIS`.

- **Portrait orientation** (`_domino_svg`): look up the file `domino_{min}_{max}.svg`.
  If `top > bottom` rotate the whole image 180° so the correct half is on top.

- **Landscape orientation** (`_domino_svg_h`): rotate the portrait image
  90° as a whole (not individual pip halves):
  - `top ≤ bottom`: CCW −90° → `transform="translate(0, pw) rotate(-90)"` so
    the top half appears on the left.
  - `top > bottom`: CW +90° → `transform="translate(ph, 0) rotate(90)"` so
    the bottom half (containing the higher-valued `top` pips) appears on the
    left.

- Doubles in the horizontal run are rendered landscape and then CSS-rotated
  90° via `_apply_bone_rotation` so they appear perpendicular to the run.

### Face-down dominoes (boneyard and computer hand)

An image in `images/dominoes_facedown/` is used as the skin for face-down
bones.  The image is large; `_load_facedown_image_uri()` reads it with Pillow,
resizes it to 200 × 400 px, and re-encodes it as a JPEG (quality 80) to keep
the embedded HTML compact.  The result is stored in the DOM element
`#facedown-image-uri` and loaded at PyScript startup into `_FACEDOWN_IMAGE_URI`.

The same rotation logic (portrait vs landscape) is applied to face-down bones.

---

## Code Conventions (PyScript)

- `_played_dominoes` — list of `[top, bottom]` pairs for the horizontal run,
  in play order (replaces the old `_chain` / `play_chain` names; a "chain"
  implies a line, but the board branches).
- `_top_branch` / `_bottom_branch` — vertical arms above/below the spinner.
- `_BONE_GAP_PX = 4` — uniform pixel gap between all adjacent dominoes.
- `_compute_bone_size()` — returns the largest half-width `w` (px, max 55)
  that fits the current number of dominoes in both the horizontal and vertical
  dimensions.

---

## Discussion Notes (architecture decisions)

- **Why embed images in the HTML?**  The game page is a self-contained temp
  file opened in the browser.  External file references would not resolve, so
  all assets must be embedded as base64 data URIs at page-generation time.

- **Why Pillow for the face-down image?**  The source PNG can be very large
  (e.g. 36 MB at 3024 × 4032 px 16-bit).  Pillow is used to resize to
  200 × 400 and re-encode as JPEG before embedding, keeping the HTML file size
  manageable.  Pillow is listed as a script dependency in the PEP 723 metadata
  and in the CI workflow's pip install step.  If Pillow is unavailable,
  `_load_facedown_image_uri()` returns `""` and face-down bones fall back to
  an empty `<image>` element.

- **"played dominoes" not "chain"**  A chain is a single line; racehorse
  dominoes can branch both horizontally (the spinner arms) and vertically
  (the spinner branches).  The data structures are named `_played_dominoes`,
  `_top_branch`, and `_bottom_branch` to reflect this.
