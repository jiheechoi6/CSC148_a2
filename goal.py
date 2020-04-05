"""CSC148 Assignment 2

=== CSC148 Winter 2020 ===
Department of Computer Science,
University of Toronto

This code is provided solely for the personal and private use of
students taking the CSC148 course at the University of Toronto.
Copying for purposes other than this use is expressly prohibited.
All forms of distribution of this code, whether as given or with
any changes, are expressly prohibited.

Authors: Diane Horton, David Liu, Mario Badr, Sophia Huynh, Misha Schwartz,
and Jaisie Sin

All of the files in this directory and all subdirectories are:
Copyright (c) Diane Horton, David Liu, Mario Badr, Sophia Huynh,
Misha Schwartz, and Jaisie Sin

=== Module Description ===

This file contains the hierarchy of Goal classes.
"""
from __future__ import annotations
import random
from typing import List, Tuple
from settings import COLOUR_LIST


def generate_goals(num_goals: int) -> List[Goal]:
    """Return a randomly generated list of goals with length num_goals.

    All elements of the list must be the same type of goal, but each goal
    must have a different randomly generated colour from COLOUR_LIST. No two
    goals can have the same colour.

    Precondition:
        - num_goals <= len(COLOUR_LIST)

    >>> goals = generate_goals(3)
    >>> len(goals)
    3
    >>> goals[0].colour == goals[1].colour
    False
    """
    # goal_type = random.choice(['perimeter', 'blob'])
    goal_type = 'blob'
    goals = []

    i = 0
    while i < num_goals:
        if goal_type == "perimeter":
            # set new color
            new_goal = PerimeterGoal(_decide_new_color(goals))
        else:
            new_goal = BlobGoal(_decide_new_color(goals))
        goals.append(new_goal)
        i += 1

    return goals


def _decide_new_color(goals: List[Goal]) -> Tuple[int, int, int]:
    """this helper function is used in generate_goals. chooses a random color
    to generate a goal in the returning list
    """
    new_color = random.choice(COLOUR_LIST)
    exist = False
    for goal in goals:
        if new_color == goal.colour:
            exist = True
            break

    if exist:
        return _decide_new_color(goals)
    else:
        return new_color


def _flatten(block: Block) -> List[List[Tuple[int, int, int]]]:
    """Return a two-dimensional list representing <block> as rows and columns of
    unit cells.

    Return a list of lists L, where,
    for 0 <= i, j < 2^{max_depth - self.level}
        - L[i] represents column i and
        - L[i][j] represents the unit cell at column i and row j.

    Each unit cell is represented by a tuple of 3 ints, which is the colour
    of the block at the cell location[i][j]

    L[0][0] represents the unit cell in the upper left corner of the Block.
    """
    length = int(2 ** (block.max_depth - block.level))
    lst = [[(1, 1, 1) for _ in range(length)] for _ in range(length)]
    if len(block.children) == 0:
        for i in range(length):
            for j in range(length):
                lst[i][j] = block.colour
        return lst
    for i in range(4):
        temp = _flatten(block.children[i])
        col_offset = 0
        row_offset = 0

        if i == 2:
            col_offset = length // 2
        elif i == 0:
            row_offset = length // 2
        elif i == 3:
            row_offset = length // 2
            col_offset = length // 2

        for j in range(length//2):
            for k in range(length//2):
                lst[row_offset+j][col_offset+k] = temp[j][k]

    return lst


class Goal:
    """A player goal in the game of Blocky.

    This is an abstract class. Only child classes should be instantiated.

    === Attributes ===
    colour:
        The target colour for this goal, that is the colour to which
        this goal applies.
    """
    colour: Tuple[int, int, int]

    def __init__(self, target_colour: Tuple[int, int, int]) -> None:
        """Initialize this goal to have the given target colour.
        """
        self.colour = target_colour

    def score(self, board: Block) -> int:
        """Return the current score for this goal on the given board.

        The score is always greater than or equal to 0.
        """
        raise NotImplementedError

    def description(self) -> str:
        """Return a description of this goal.
        """
        raise NotImplementedError


class PerimeterGoal(Goal):
    """
    child class of goal used to calculate perimeter goal
    """
    def score(self, board: Block) -> int:
        # TODO: Implement me
        score = 0
        bord = _flatten(board)
        for i in range(len(bord)):
            for p in range(len(bord[i])):
                if i == 0 and p == 0 and bord[i][p] == self.colour:
                    score += 2
                elif i == 0 and p == len(bord[i])-1 and bord[i][p] \
                        == self.colour:
                    score += 2
                elif i == len(bord[i])-1 and p == len(bord[i])-1 and \
                        bord[i][p] == self.colour:
                    score += 2
                elif i == len(bord[i])-1 and p == 0 and bord[i][p] \
                        == self.colour:
                    score += 2
                elif i == 0 and bord[i][p] == self.colour:
                    score += 1
                elif p == 0 and bord[i][p] == self.colour:
                    score += 1
                elif i == len(bord)-1 and bord[i][p] == self.colour:
                    score += 1
                elif p == len(bord[i])-1 and bord[i][p] == self.colour:
                    score += 1
        return score

    def description(self) -> str:
        return 'The perimeter target for this game'  # FIXME


class BlobGoal(Goal):
    """
    Class for calculating blob goal
    """
    def score(self, board: Block) -> int:
        flat = _flatten(board)
        visited = [[-1 for _ in range(len(flat))] for _ in range(len(flat))]
        results = []
        for i in range(len(flat)):
            for p in range(len(flat)):
                results.append(self._undiscovered_blob_size((i, p),
                                                            flat, visited))
        return max(results)

    def _undiscovered_blob_size(self, pos: Tuple[int, int],
                                board: List[List[Tuple[int, int, int]]],
                                visited: List[List[int]]) -> int:
        """Return the size of the largest connected blob that (a) is of this
        Goal's target colour, (b) includes the cell at <pos>, and (c) involves
        only cells that have never been visited.

        If <pos> is out of bounds for <board>, return 0.

        <board> is the flattened board on which to search for the blob.
        <visited> is a parallel structure that, in each cell, contains:
            -1 if this cell has never been visited
            0  if this cell has been visited and discovered
               not to be of the target colour
            1  if this cell has been visited and discovered
               to be of the target colour

        Update <visited> so that all cells that are visited are marked with
        either 0 or 1.
        """
        if pos[0] < 0 or pos[0] >= len(board) or pos[1] < 0 or pos[1] \
                >= len(board):
            return 0
        if visited[pos[0]][pos[1]] != -1:
            return 0
        if board[pos[0]][pos[1]] != self.colour:
            visited[pos[0]][pos[1]] = 0
            return 0
        else:
            count = 1
            visited[pos[0]][pos[1]] = 1
            count += self._undiscovered_blob_size((pos[0] - 1, pos[1]),
                                                  board, visited)
            count += self._undiscovered_blob_size((pos[0] + 1, pos[1]),
                                                  board, visited)
            count += self._undiscovered_blob_size((pos[0], pos[1] - 1),
                                                  board, visited)
            count += self._undiscovered_blob_size((pos[0], pos[1] + 1),
                                                  board, visited)
        return count

    def description(self) -> str:
        return 'The blob size target for this game'


if __name__ == '__main__':
    import doctest
    doctest.testmod()

    import python_ta
    python_ta.check_all(config={
        'allowed-import-modules': [
            'doctest', 'python_ta', 'random', 'typing', 'block', 'settings',
            'math', '__future__'
        ],
        'max-attributes': 15
    })
