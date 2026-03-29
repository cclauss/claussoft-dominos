from dominos_ui_on_pyscript import (
    _PYSCRIPT_CODE,
    GameState,
    all_domino_bones,
    build_html,
    deal_game,
)


def test_dominos() -> None:
    assert True


def test_all_domino_bones_count() -> None:
    """There are 28 unique domino bones (0-6)."""
    bones = all_domino_bones()
    assert len(bones) == 28
    # Each bone is unique
    assert len({tuple(t) for t in bones}) == 28


def test_deal_game_distributes_bones() -> None:
    state = deal_game()
    assert len(state.player0_hand) == 7
    assert len(state.player1_hand) == 7
    assert len(state.boneyard) == 14
    all_bones = state.player0_hand + state.player1_hand + state.boneyard
    assert len(all_bones) == 28


def test_deal_game_no_duplicates() -> None:
    state = deal_game()
    all_bones = state.player0_hand + state.player1_hand + state.boneyard
    canonical = {(min(a, b), max(a, b)) for a, b in all_bones}
    assert len(canonical) == 28


def test_game_state_default_scores() -> None:
    state = deal_game()
    assert state.scores == [0, 0]
    assert state.current_player == 0


def test_game_state_serialization() -> None:
    state = deal_game()
    data = state.model_dump_json()
    restored = GameState.model_validate_json(data)
    assert restored.player0_hand == state.player0_hand
    assert restored.player1_hand == state.player1_hand
    assert restored.boneyard == state.boneyard
    assert restored.scores == [0, 0]


def test_game_state_game_num_default() -> None:
    """game_num starts at 0 (human plays first in the first hand)."""
    state = deal_game()
    assert state.game_num == 0


def test_game_state_game_num_serialization() -> None:
    """game_num survives a JSON round-trip."""
    state = GameState(
        player0_hand=[[0, 0]],
        player1_hand=[[0, 1]],
        boneyard=[[0, 2]],
        game_num=3,
    )
    restored = GameState.model_validate_json(state.model_dump_json())
    assert restored.game_num == 3


def test_html_status_msg_is_scrollable_div() -> None:
    """The status message area is rendered as a <div> (not a <span>) for scrolling."""
    state = deal_game()
    html = build_html(state)
    # Must be a <div> so CSS overflow-y can scroll the message history.
    assert '<div id="status-msg">' in html
    # The initial message is wrapped in a <p> for consistent append behaviour.
    assert "<p>" in html


def test_html_boneyard_pyscript_always_face_down() -> None:
    """_PYSCRIPT_CODE always renders boneyard bones face-down."""
    # face_down=True must appear in the boneyard render path.
    assert "face_down=True" in _PYSCRIPT_CODE
    # The old face_down=not draggable_to_hand pattern must NOT be present.
    assert "face_down=not draggable_to_hand" not in _PYSCRIPT_CODE


def test_html_boneyard_random_draw() -> None:
    """Boneyard draw picks a random bone (not a specific user-chosen one)."""
    # Random index pick must be present in the drop handler.
    assert "random.randrange(len(_boneyard))" in _PYSCRIPT_CODE
    # Drag data must not expose pip values (only the generic draw signal).
    assert "boneyard:draw" in _PYSCRIPT_CODE


def test_html_ambiguous_play_check() -> None:
    """Play area drop handler guards against ambiguous multi-end placement."""
    assert "_is_ambiguous_play" in _PYSCRIPT_CODE
    assert "_on_drop_chain_bone" in _PYSCRIPT_CODE
    # target_end parameter is required for directed placement.
    assert "target_end=" in _PYSCRIPT_CODE


def test_html_game_num_alternates_first_player() -> None:
    """_deal_new_hand increments _game_num and picks first player accordingly."""
    assert "_game_num += 1" in _PYSCRIPT_CODE
    assert "_game_num % 2" in _PYSCRIPT_CODE
