from dominos_ui_on_pyscript import (
    GameState,
    all_domino_tiles,
    deal_game,
)


def test_dominos() -> None:
    assert True


def test_all_domino_tiles_count() -> None:
    """There are 28 unique domino tiles (0-6)."""
    tiles = all_domino_tiles()
    assert len(tiles) == 28
    # Each tile is unique
    assert len({tuple(t) for t in tiles}) == 28


def test_deal_game_distributes_tiles() -> None:
    state = deal_game()
    assert len(state.player0_hand) == 7
    assert len(state.player1_hand) == 7
    assert len(state.boneyard) == 14
    all_tiles = state.player0_hand + state.player1_hand + state.boneyard
    assert len(all_tiles) == 28


def test_deal_game_no_duplicates() -> None:
    state = deal_game()
    all_tiles = state.player0_hand + state.player1_hand + state.boneyard
    canonical = {(min(a, b), max(a, b)) for a, b in all_tiles}
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
