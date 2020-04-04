from typing import List, Optional, Tuple
import os
import pygame
import pytest

from block import Block
from blocky import _block_to_squares
from goal import BlobGoal, PerimeterGoal, _flatten
from player import _get_block, create_players, HumanPlayer, RandomPlayer, SmartPlayer
from renderer import Renderer
from settings import COLOUR_LIST


def set_children(block: Block, colours: List[Optional[Tuple[int, int, int]]]) \
        -> None:
    """Set the children at <level> for <block> using the given <colours>.

    Precondition:
        - len(colours) == 4
        - block.level + 1 <= block.max_depth
    """
    size = block._child_size()
    positions = block._children_positions()
    level = block.level + 1
    depth = block.max_depth

    block.children = []  # Potentially discard children
    for i in range(4):
        b = Block(positions[i], size, colours[i], level, depth)
        block.children.append(b)


@pytest.fixture
def board_16x16() -> Block:
    """Create a reference board with a size of 750 and a max_depth of 2.
    """
    # Level 0
    board = Block((0, 0), 750, None, 0, 3)

    # Level 1
    colours = [None, COLOUR_LIST[2], COLOUR_LIST[1], COLOUR_LIST[3]]
    set_children(board, colours)

    # Level 2
    colours = [COLOUR_LIST[0], None, COLOUR_LIST[1], COLOUR_LIST[3]]
    set_children(board.children[0], colours)

    # Level 3
    colours = [COLOUR_LIST[0], COLOUR_LIST[1], COLOUR_LIST[2], COLOUR_LIST[3]]
    set_children(board.children[0].children[1], colours)

    return board


@pytest.fixture
def single_board() -> Block:
    return Block((0, 0), 750, COLOUR_LIST[0], 0, 0)


@pytest.fixture
def board_4x4() -> Block:
    board = Block((0, 0), 750, None, 0, 1)

    colours = [COLOUR_LIST[0], COLOUR_LIST[1], COLOUR_LIST[2], COLOUR_LIST[3]]
    set_children(board, colours)

    return board


@pytest.fixture
def board_16x16_rotate1() -> Block:
    """Create a reference board with a size of 750 and a max_depth of 2.
    """
    # Level 0
    board = Block((0, 0), 750, None, 0, 3)

    # Level 1
    colours = [COLOUR_LIST[2], COLOUR_LIST[1], COLOUR_LIST[3], None]
    set_children(board, colours)

    # Level 2
    colours = [None, COLOUR_LIST[1], COLOUR_LIST[3], COLOUR_LIST[0]]
    set_children(board.children[3], colours)

    # Level 3
    colours = [COLOUR_LIST[1], COLOUR_LIST[2], COLOUR_LIST[3], COLOUR_LIST[0]]
    set_children(board.children[3].children[0], colours)

    return board


@pytest.fixture
def board_16x16_rotate3() -> Block:
    """Create a reference board with a size of 750 and a max_depth of 2.
    """
    # Level 0
    board = Block((0, 0), 750, None, 0, 3)

    # Level 1
    colours = [COLOUR_LIST[3], None, COLOUR_LIST[2], COLOUR_LIST[1]]
    set_children(board, colours)

    # Level 2
    colours = [COLOUR_LIST[3], COLOUR_LIST[0], None, COLOUR_LIST[1]]
    set_children(board.children[1], colours)

    # Level 3
    colours = [COLOUR_LIST[3], COLOUR_LIST[0], COLOUR_LIST[1], COLOUR_LIST[2]]
    set_children(board.children[1].children[2], colours)

    return board


@pytest.fixture
def board_16x16_swap0() -> Block:
    """Create a reference board that is swapped along the horizontal plane.
    """
    # Level 0
    board = Block((0, 0), 750, None, 0, 3)

    # Level 1
    colours = [COLOUR_LIST[2], None, COLOUR_LIST[3], COLOUR_LIST[1]]
    set_children(board, colours)

    # Level 2
    colours = [COLOUR_LIST[0], None, COLOUR_LIST[1], COLOUR_LIST[3]]
    set_children(board.children[1], colours)

    # Level 3
    colours = [COLOUR_LIST[0], COLOUR_LIST[1], COLOUR_LIST[2], COLOUR_LIST[3]]
    set_children(board.children[1].children[1], colours)

    return board


@pytest.fixture
def board_16x16_swap1() -> Block:
    """Create a reference board that is swapped along the horizontal plane.
    """
    # Level 0
    board = Block((0, 0), 750, None, 0, 3)

    # Level 1
    colours = [COLOUR_LIST[3], COLOUR_LIST[1], COLOUR_LIST[2], None]
    set_children(board, colours)

    # Level 2
    colours = [COLOUR_LIST[0], None, COLOUR_LIST[1], COLOUR_LIST[3]]
    set_children(board.children[3], colours)

    # Level 3
    colours = [COLOUR_LIST[0], COLOUR_LIST[1], COLOUR_LIST[2], COLOUR_LIST[3]]
    set_children(board.children[3].children[1], colours)

    return board


def test_board_16x16_swap0(board_16x16, board_16x16_swap0) -> None:
    board_16x16.swap(0)
    assert board_16x16 == board_16x16_swap0


def test_board_16x16_swap1(board_16x16, board_16x16_swap1) -> None:
    board_16x16.swap(1)
    assert board_16x16 == board_16x16_swap1


def test_board_16x16_rotate1(board_16x16, board_16x16_rotate1) -> None:
    board_16x16.rotate(1)
    assert board_16x16 == board_16x16_rotate1


def test_board_16x16_rotate3(board_16x16, board_16x16_rotate3) -> None:
    board_16x16.rotate(3)
    assert board_16x16 == board_16x16_rotate3


def test_get_block_top_top_left(board_16x16) -> None:
    top_left = (0, 0)
    board0 = _get_block(board_16x16, top_left, 0)
    board1 = _get_block(board_16x16, top_left, 1)
    board2 = _get_block(board_16x16, top_left, 2)
    assert board0 == board_16x16
    assert board1 == board_16x16.children[1]
    assert board2 is None


def test_get_block_bottom_right(board_16x16) -> None:
    bottom_right = (board_16x16.size, board_16x16.size)
    middle = (round(board_16x16.size / 2), round(board_16x16.size / 2))
    board = _get_block(board_16x16, bottom_right, 0)
    board3 = _get_block(board_16x16, middle, 1)
    assert board is None
    assert board3 == board_16x16.children[3]


def test_get_block_middle(board_16x16) -> None:
    middle = (round(board_16x16.size / 2), 0)
    board0 = _get_block(board_16x16, middle, 0)
    board1 = _get_block(board_16x16, middle, 1)
    board2 = _get_block(board_16x16, middle, 2)
    board3 = _get_block(board_16x16, middle, 3)
    board4 = _get_block(board_16x16, middle, 4)
    assert board0 == board_16x16
    assert board1 == board_16x16.children[0]
    assert board2 == board_16x16.children[0].children[1]
    assert board3 == board_16x16.children[0].children[1].children[1]
    assert board4 is None


def test_get_block_middle2(board_16x16) -> None:
    middle = (round(board_16x16.size / 2) + round(board_16x16.size / 8), round(board_16x16.size / 8))
    board = _get_block(board_16x16, middle, 3)
    assert board == board_16x16.children[0].children[1].children[3]


def test_flatten_single_board(single_board) -> None:
    assert [[COLOUR_LIST[0]]] == _flatten(single_board)


def test_flatten_board_4x4(board_4x4) -> None:
    result = _flatten(board_4x4)
    print(result)
    assert result == [[COLOUR_LIST[1], COLOUR_LIST[2]],
                      [COLOUR_LIST[0], COLOUR_LIST[3]]]


def test_flatten_board_16x16(board_16x16) -> None:
    result = _flatten(board_16x16)
    exp = [[COLOUR_LIST[2] for _ in range(4)] + [COLOUR_LIST[1] for _ in range(4)],
           [COLOUR_LIST[2] for _ in range(4)] + [COLOUR_LIST[1] for _ in range(4)],
           [COLOUR_LIST[2] for _ in range(4)] + [COLOUR_LIST[1] for _ in range(4)],
           [COLOUR_LIST[2] for _ in range(4)] + [COLOUR_LIST[1] for _ in range(4)],
           [COLOUR_LIST[1], COLOUR_LIST[2], COLOUR_LIST[1], COLOUR_LIST[1]] + [COLOUR_LIST[3] for _ in range(4)],
           [COLOUR_LIST[0], COLOUR_LIST[3], COLOUR_LIST[1], COLOUR_LIST[1]] + [COLOUR_LIST[3] for _ in range(4)],
           [COLOUR_LIST[0], COLOUR_LIST[0], COLOUR_LIST[3], COLOUR_LIST[3]] + [COLOUR_LIST[3] for _ in range(4)],
           [COLOUR_LIST[0], COLOUR_LIST[0], COLOUR_LIST[3], COLOUR_LIST[3]] + [COLOUR_LIST[3] for _ in range(4)]]
    print(result)
    assert result == exp


def test_create_players() -> None:
    players = create_players(1, 2, [2])
    exp = [1, 2, 1]
    result = [0, 0, 0]
    for player in players:
        if isinstance(player, HumanPlayer):
            result[0] += 1
        elif isinstance(player, RandomPlayer):
            result[1] += 1
        elif isinstance(player, SmartPlayer):
            result[2] += 1
    result_id = []
    exp_id = [i for i in range(4)]
    for player in players:
        result_id.append(player.id)
    assert exp == result
    assert exp_id == result_id


def test_perimeter_goal_single_board(single_board) -> None:
    correct_scores = [
        (COLOUR_LIST[0], 2),
        (COLOUR_LIST[1], 0),
        (COLOUR_LIST[2], 0),
        (COLOUR_LIST[3], 0)
    ]

    # Set up a goal for each colour and check the results
    for colour, expected in correct_scores:
        goal = PerimeterGoal(colour)
        assert goal.score(single_board) == expected


def test_perimeter_goal_board_4x4(board_4x4) -> None:
    correct_scores = [
        (COLOUR_LIST[0], 2),
        (COLOUR_LIST[1], 2),
        (COLOUR_LIST[2], 2),
        (COLOUR_LIST[3], 2)
    ]

    # Set up a goal for each colour and check the results
    for colour, expected in correct_scores:
        goal = PerimeterGoal(colour)
        assert goal.score(board_4x4) == expected


def test_perimeter_goal_board_16x16(board_16x16) -> None:
    correct_scores = [
        (COLOUR_LIST[0], 5),
        (COLOUR_LIST[1], 9),
        (COLOUR_LIST[2], 8),
        (COLOUR_LIST[3], 10)
    ]

    # Set up a goal for each colour and check the results
    for colour, expected in correct_scores:
        goal = PerimeterGoal(colour)
        assert goal.score(board_16x16) == expected


def test_create_copy(board_16x16, single_board, board_4x4) -> None:
    exp1 = board_16x16.create_copy()
    exp2 = single_board.create_copy()
    exp3 = board_4x4.create_copy()
    assert board_16x16 == exp1
    assert id(board_16x16) != id(exp1)
    assert single_board == exp2
    assert id(single_board) != id(exp2)
    assert board_4x4 == exp3
    assert id(board_4x4) != id(exp3)


def test_blob_goal_single_board(single_board) -> None:
    correct_scores = [
        (COLOUR_LIST[0], 1),
        (COLOUR_LIST[1], 0),
        (COLOUR_LIST[2], 0),
        (COLOUR_LIST[3], 0)
    ]

    # Set up a goal for each colour and check the results
    for colour, expected in correct_scores:
        goal = BlobGoal(colour)
        assert goal.score(single_board) == expected


def test_blob_goal_board_4x4(board_4x4) -> None:
    correct_scores = [
        (COLOUR_LIST[0], 1),
        (COLOUR_LIST[1], 1),
        (COLOUR_LIST[2], 1),
        (COLOUR_LIST[3], 1)
    ]

    # Set up a goal for each colour and check the results
    for colour, expected in correct_scores:
        goal = BlobGoal(colour)
        assert goal.score(board_4x4) == expected


def test_blob_goal_board_16x16(board_16x16) -> None:
    correct_scores = [
        (COLOUR_LIST[0], 5),
        (COLOUR_LIST[1], 16),
        (COLOUR_LIST[2], 17),
        (COLOUR_LIST[3], 20)
    ]

    # Set up a goal for each colour and check the results
    for colour, expected in correct_scores:
        goal = BlobGoal(colour)
        assert goal.score(board_16x16) == expected


if __name__ == '__main__':
    import pytest
    pytest.main(['tests.py'])
