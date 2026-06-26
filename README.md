# Spider Solitaire (1-Suit) Simulation in Arena/Python

## Overview

This project implements a simplified **1-Suit Spider Solitaire** simulation using **Rockwell Arena Simulation Software** as part of the Georgia Institute of Technology **ISYE 6644 – Simulation** course.

Unlike an interactive solitaire game, this project models the game as a **Discrete Event Simulation (DES)**. Cards are represented as entities and game actions are simulated using Arena modules.

The objective is to evaluate the performance of a rule-based playing strategy through repeated simulation runs.

---

## Objectives

- Model the rules of 1-Suit Spider Solitaire using Arena.
- Simulate thousands of randomized games.
- Estimate the probability of winning.
- Analyze game performance using Arena statistical outputs.

---

## Game Rules

- 104 cards (8 identical suits)
- 10 tableau columns
- Initial deal:
  - Columns 1–4 receive 6 cards
  - Columns 5–10 receive 5 cards
- Remaining cards stay in stock.
- Cards are built downward by rank.
- Complete sequences from King to Ace are removed.
- The game ends when:
  - Eight complete sequences are removed (Win)
  - No legal moves remain and stock is empty (Loss)

---

## Arena/Python Model

### Main Flow

```
Create Cards
      ↓
Assign Card Attributes
      ↓
Randomize Deck
      ↓
Deal Initial Tableau
      ↓
Search for Valid Move
      ↓
Move Card
      ↓
Check Completed Sequence
      ↓
Remove Sequence
      ↓
Game Complete?
      ↓
Deal from Stock (if needed)
      ↓
Repeat
```

---

## Arena/Python Modules Used

| Module | Purpose |
|---------|----------|
| Create | Generate 104 card entities |
| Assign | Assign rank, suit, column, face-up status |
| Decide | Check move legality and game conditions |
| Process | Shuffle / deck management |
| Record | Record statistics |
| Dispose | End simulation |

---

## Variables

### Global Variables

| Variable | Description |
|-----------|-------------|
| vMoves | Total moves made |
| vCompletedSets | Number of completed King-Ace sequences |
| vStockCount | Cards remaining in stock |
| vGameWon | Win indicator |

---

### Arrays

```
vColumn(10,20)
```

Stores the cards currently located in each tableau column.

```
vStock(50)
```

Stores remaining stock cards.

---

## Entity Attributes

| Attribute | Description |
|-----------|-------------|
| aRank | Card rank (1–13) |
| aSuit | Suit ID |
| aColumn | Current tableau column |
| aFaceUp | Face-up status |
| aShuffle | Random shuffle value |

---

## Playing Strategy

The simulation follows a deterministic rule-based strategy.

Priority:

1. Complete a King-to-Ace sequence
2. Reveal hidden cards
3. Extend descending sequences
4. If no move exists, deal from stock

This is intentionally simple to allow statistical evaluation.

---

## Performance Measures

Arena records:

- Probability of winning
- Average moves per game
- Average completed sequences
- Average stock deals used
- Probability of getting stuck

---

## Assumptions

- Single-suit Spider Solitaire
- One-card movement only (simplified)
- No user interaction
- Rule-based AI player
- Randomized deck each replication

---

## Running the Model

1. Open the Arena model (`.doe`).
2. Set desired number of replications.
3. Run the simulation.
4. Review Arena output reports.

---

## Future Improvements

- Multi-card movement
- Four-suit Spider Solitaire
- Smarter move-selection heuristics
- Monte Carlo strategy comparison
- Genetic Algorithm optimization
- Reinforcement Learning player

---

## Repository Structure

```
SpiderSolitaireArena/
│
├── README.md
├── Arena/
│   ├── SpiderSolitaire.doe
│   └── SpiderSolitaire.mod
├── Python/
│   └── main.py
├── Documentation/
│   ├── Project_Report.pdf
│   ├── Flowchart.png
│   └── Arena_Diagram.png
│
├── Results/
│   ├── OutputReport.pdf
│   ├── WinRate.xlsx
│   └── Charts/
│
└── Images/
    ├── ArenaModel.png
    └── SpiderLayout.png
```

---

## Example Statistics

| Metric | Example |
|--------|---------|
| Replications | 10,000 |
| Win Rate | 31.4% |
| Avg Moves | 268 |
| Avg Completed Sets | 6.7 |
| Avg Stock Deals | 3.8 |

*(Illustrative values only.)*

---

## Technologies

- Arena
- Arena Basic Process Modules
- Microsoft Excel
- GitHub

---

## Authors

**Group 70: Dinh Tran, Omid Morshed, Lizhi Qin, Yeyan Wang**
Georgia Institute of Technology
---
## License

This project is for educational purposes as part of **ISYE 6644 – Simulation**.
