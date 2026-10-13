# Policies

These rules keep the competition about learned models, keep evaluation feasible, and keep it
fair. If you are unsure whether something is allowed, ask on Canvas **before** relying on it.

## At play time (inside your agent)

Your agent is the code around your core model, and you design it. It may include:

- encoding the observation, memory of past observations, belief tracking about hidden pieces;
- the game rules themselves: which moves are legal, and that capturing a visible king wins the game;
- search, sampling, or ensembles, **as long as every judgment of how good a position or move
  is comes from your own core model** (all networks count toward your parameter count);
- any amount of computation that fits the time control.

It may not include:

- Stockfish or any other chess engine or game-playing program you did not train, in any form;
- hand-written evaluation functions or move preferences (material counts, piece-square tables,
  "always capture the queen" rules); the rules of the game are fine, judgment is not;
- opening books or tables of stored moves or positions;
- network access, files outside your agent directory, or information carried between games.

## At training time

You may use:

- Stockfish or any other chess engine, at any strength, as a teacher;
- public chess data (for example the Lichess game database);
- the reference bots and this repository's code;
- self-play, reinforcement learning, distillation;
- pretrained models with a license that allows it (any part used at play time counts toward your parameters).

You may not use:

- Fog-of-War-specific engines, models or game collections made by others;
- other students' code, weights, data or results. Discussing ideas is fine; say who you
  discussed with in your journal.

## Compute

- Train on your Sol class account (`-q class`). Its limits apply to everyone equally.
- If you use any other hardware, list it with its GPU-hours in `submission/MODEL.md`.
- Record the compute of every training run in your journal.

## AI assistants

You **may** use AI assistants and coding agents to write code, debug, and explore ideas. It is
a normal part of the work now, and learning to direct these tools well is part of the point.

You **must**:

- **Disclose** in [`AI_USE.md`](../AI_USE.md): which tools you used, for what, and roughly how much.
- **Mark agent-written commits** with a trailer naming the tool, for example
  `Co-Authored-By: <tool name>`.
- **Write your own journal entries:** the hypotheses, the decisions, and why. AI-generated text
  in the journal must be marked as such.
- **Be able to explain** every part of your submission.

Expect this: a coding agent can produce a working pipeline at roughly the baseline's level in an
afternoon. What it cannot do for you is decide what to try next with limited compute and tell
a real improvement from noise. That judgment is what your journal, report and grade are about.

Hiding AI use, or submitting work you cannot explain, is an academic integrity violation.

## Verification

- **Retraining checks:** the staff may retrain any entry from its repository with its
  documented script and seeds, and check that the result plays at a similar level. This
  includes every top-10 entry.
- **Top-10 walkthrough:** before extra credit is awarded, each top-10 student gives a live
  10–15 minute walkthrough: one design decision, one failed experiment, and questions about
  their own code.
- **Violations:** entries that break these rules are removed from the ladder and handled under
  the ASU academic integrity policy.
