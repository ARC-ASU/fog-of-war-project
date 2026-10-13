# Policies

These rules keep the competition about learned models, keep evaluation feasible, and keep it
fair. If you are unsure whether something is allowed, ask on Canvas **before** relying on it.

## At play time (inside your agent)

Your agent is the code around your core model, and you design it. It may include:

- encoding the observation, memory of past observations, belief tracking about hidden pieces;
- the game rules themselves: which moves are legal, and that capturing a visible king wins the game;
- search, sampling, or ensembles, **as long as every judgment of how good a position or move
  is comes from your own neural networks** (all of them count toward your parameter count;
  see "Core models" in [COMPETITION.md](COMPETITION.md));
- any amount of computation that fits the per-move FLOP budget.

It may not include:

- Stockfish or any other chess engine or game-playing program you did not train, in any form;
- hand-written evaluation functions or move preferences (material counts, piece-square tables,
  "always capture the queen" rules); the rules of the game are fine, judgment is not;
- any learned component that is not a neural network in your submission's weight files: no
  decision trees, nearest-neighbour lookups, or statistics gathered from games;
- opening books or tables of stored moves or positions;
- network computation outside PyTorch in the thread that calls `act` (it would escape the FLOP
  count; see [COMPETITION.md](COMPETITION.md));
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

## Your repository and commit history

Your GitHub repository is the record of your project, and the staff will read it. Keep it
**actively committed and pushed** so that anyone can follow how your agent came to be, one
step at a time.

- **One logical step per commit.** A commit does one thing (a new feature encoding, a training
  script change, a bug fix, a new experiment config). Its message says what changed and why,
  for example `Add value head to policy net to train on game outcomes`. Don't mix unrelated
  changes, and don't sit on a week of work and commit it as one dump.
- **Push as you go.** Push at the end of every working session. At the least, there must be
  pushed commits in **every week** from the proposal (Oct 23) to the model freeze (Dec 4).
  A history that is empty and then appears all at once near a deadline will be questioned.
- **Never rewrite pushed history.** No force-pushes, and no squashing or rebasing commits you
  have already pushed. Fix mistakes with new commits.
- **Link experiments to commits.** Every journal entry names the commit it ran at, so each
  result can be reproduced from the exact code.
- **Commit what is needed to reproduce your work:** code, configs, training commands and seeds,
  logs and small result files. Don't commit large datasets or secrets (API keys, tokens).
  Put weights over 100 MB in release assets.
- **Mark AI-written commits.** Commits written mostly by a coding agent carry a trailer naming
  it (see below).
- **Staff access:** your repository is private, the course staff are collaborators, and they
  may read it at any time. The commit history is part of how your work is graded
  ([GRADING.md](GRADING.md)) and how its authenticity is verified.

## AI assistants

You **may** use AI assistants and coding agents to write code, debug, and explore ideas. It is
a normal part of the work now, and learning to direct these tools well is part of the point.
[RESOURCES.md](RESOURCES.md#ai-assistants) lists the free tools ASU provides to every student.

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
- **Violations:** entries that break these rules are removed from the tournaments and handled under
  the ASU academic integrity policy.
