# Connect4 with AI

A small Python project for experimenting with **adversarial search algorithms** through a three-player, 10×10 Connect Four variant.

Two players are human (`X` and `O`) and the third player (`R`) is controlled by an AI that uses **depth-limited Minimax with alpha-beta pruning**. The project intentionally stays compact so the search logic, heuristic evaluation, and game loop are easy to inspect in one file.

## Screenshots

The repository is prepared for two screenshots:

| Random turns | Round-robin turns |
| --- | --- |
| ![Random-turn mode](assets/screenshots/random-turns.png) | ![Round-robin mode](assets/screenshots/round-robin.png) |

Replace the two placeholder images in `assets/screenshots/` with your own screenshots using the same filenames and GitHub will display them here automatically.

## Why this project exists

The main purpose of this project is to practice and visualize how a game-playing AI makes decisions with Minimax. Connect Four provides a simple board state and a clear win condition, while the third player and alternative turn modes make the search problem a little less conventional than standard two-player Connect Four.

The GUI is intentionally simple. It exists mainly to make the AI behavior observable: you can play against it, see which column it chooses, and see how long each AI decision takes.

## Players and colors

| Symbol | Role | Color |
| --- | --- | --- |
| `X` | Human player 1 | Red |
| `O` | Human player 2 | Green |
| `R` | AI player | Yellow |

A player wins by connecting four pieces horizontally, vertically, or diagonally.

## Game modes

The GUI provides two ways to choose the next player. The game rules and AI algorithm are otherwise unchanged.

### Random turns

This is the original mode. Before every move, the next player is selected randomly from `X`, `O`, and `R`, similar to rolling a three-sided die.

To prevent one player from dominating the game only because of luck, the same player cannot be selected more than two times in a row.

### Round-robin turns

Players move in a fixed repeating order:

```text
X → O → R → X → O → R → ...
```

This mode removes randomness from turn selection and makes the game easier to follow when observing the AI's choices.

The selected mode controls the **game loop only**. The Minimax implementation itself is intentionally kept the same in both modes.

## How the AI works

The AI controls `R`. Whenever it receives a turn, it evaluates the legal columns and searches possible future board states before selecting a move.

### 1. Generate legal moves

The AI starts with every column that is not full. At the top level, the columns are ordered roughly from the center outward. Trying promising moves earlier can allow alpha-beta pruning to discard more branches later in the search.

### 2. Search with Minimax

The search uses a fixed depth of `4`.

- The **maximizing** layer represents the AI (`R`) and tries to find the highest-scoring board state.
- The **minimizing** layer represents the human opponents (`X` and `O`) and searches for moves that reduce the AI's score.
- A guaranteed AI win evaluates to positive infinity.
- A guaranteed human win evaluates to negative infinity.
- If the depth limit is reached first, the board is scored with the heuristic evaluation function.

Conceptually, the AI is asking:

```text
If I play here, what is the strongest response my opponents could make,
and what position would that leave me in after a few more moves?
```

It chooses the move whose worst-case continuation has the best evaluation for `R`.

### 3. Evaluate non-terminal positions

When the search reaches its depth limit, the heuristic scans possible four-cell lines in four directions:

- horizontal
- vertical
- diagonal down-right
- diagonal down-left

For uncontested lines, the score grows as a player gets closer to four connected pieces:

| Pieces in a candidate line | Score magnitude |
| ---: | ---: |
| 1 | 1 |
| 2 | 5 |
| 3 | 50 |

Lines belonging to `R` add to the score. Lines belonging to either human player subtract from it. Lines containing pieces from both sides are ignored because that four-cell window can no longer become a clean four-in-a-row for one side.

### 4. Alpha-beta pruning

Minimax can expand many board states even at a modest depth. Alpha-beta pruning tracks the best result already available to the maximizing and minimizing sides.

When a branch cannot possibly improve the final decision, that branch is stopped early instead of being searched completely. This reduces unnecessary work without changing the result that Minimax would choose for the same search model and depth.

### Search-model limitation

The real game has three players, and the random-turn mode also has stochastic turn selection. The current Minimax tree deliberately uses a simpler adversarial model: `R` is the maximizer, while both `X` and `O` are treated as minimizing opponents.

The search therefore does **not** simulate the random die or the exact round-robin turn order inside the tree. Those mechanics are handled by the game loop. Keeping that distinction explicit is useful here because the repository is focused on practicing Minimax, alpha-beta pruning, and heuristic design rather than implementing a full stochastic multi-agent search algorithm.

## UI details

- Columns are displayed as `1` through `10` for the player.
- Internal Python indexing still uses `0` through `9`.
- The player legend shows the symbol, role, and color for `X`, `O`, and `R`.
- The status line shows the active game mode and current player.
- After an AI move, the status line shows the selected column and decision time.
- You can select a mode and use **Start / Restart Game** to reset the board with that mode.

## Requirements

- Python 3
- NumPy 2.3.5
- Tkinter

The dependency is pinned in `requirements.txt`:

```text
numpy==2.3.5
```

Tkinter is included with many Python installations. On some Linux distributions it may need to be installed separately, for example through the system package `python3-tk`.

## Installation

Clone the repository and enter the project directory:

```bash
git clone <your-repository-url>
cd Connect4-With-Ai
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows:

```bash
.venv\Scripts\activate
```

Or on macOS/Linux:

```bash
source .venv/bin/activate
```

Install the dependency:

```bash
pip install -r requirements.txt
```

## Run

```bash
python connect4.py
```

Choose either **Random turns** or **Round-robin**, then click **Start / Restart Game**.

When `X` or `O` receives a turn, use the numbered buttons below the board to choose a column. When `R` receives a turn, the AI automatically searches for and plays a move.

## Project structure

```text
.
├── assets/
│   └── screenshots/
│       ├── random-turns.png
│       └── round-robin.png
├── .gitignore
├── README.md
├── connect4.py
└── requirements.txt
```

## Possible experiments

Because the project is centered on search algorithms, a few parameters are easy to experiment with without redesigning the application:

- change `AI_DEPTH` and compare decision time versus playing strength
- change the heuristic weights (`1`, `5`, `50`)
- compare center-first move ordering with natural column order
- count searched or pruned nodes
- replace the simplified opponent model with a turn-aware or stochastic search algorithm

These are intentionally left as experiments rather than hidden behind a larger application architecture.
