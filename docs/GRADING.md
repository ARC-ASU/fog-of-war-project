# Grading

The project is individual and worth **20 points** of your course grade. Points come from the
quality of your work as documented in your repository, journal, report and presentation. Your
ladder rank affects only the extra credit below.

| Component | Points | Due |
|---|---:|---|
| Proposal | 2 | Fri Oct 30, 11:59 PM |
| Checkpoint | 2 | Tue Nov 17, 11:59 PM |
| Implementation and reproducibility | 4 | final |
| Experimental design and evaluation | 4 | final |
| Results analysis and limitations | 4 | final |
| Final report and recorded presentation | 4 | Sat Dec 12, 11:59 PM |

Milestone dates are fixed; the 24-hour grace period for labs does not apply.

## Proposal (2 points)

Submit a link to your repository (with staff access) and a PDF of at most 2 pages with:

- **The baseline, reproduced:** you ran `agents/baseline` (or your copy in `submission/`)
  against the reference bots with `python -m fow.arena`, and you report its local rating.
- **Your plan:** two or three concrete ideas you will test first, each with what you expect
  to happen and how you will measure it.
- **Your compute budget:** what you expect to run on Sol.
- **A journal:** `JOURNAL.md` has started.
- **A pushed history:** your commits so far are pushed, following
  [the commit rules](POLICIES.md#your-repository-and-commit-history).

## Checkpoint (2 points)

- **A valid ladder entry:** at least one `ladder-` release that passes `fow.validate`.
- **One completed experiment:** at least one idea from your plan tested, with the result in
  your journal, including what you will change next.

## Implementation and reproducibility (4 points)

- Your final entry is valid and runs within the limits.
- `submission/MODEL.md` is complete.
- Your training can be reproduced from your repository with the documented commands and
  seeds, and the result plays at a similar level.
- Your code is readable.
- **Your commit history** shows the work step by step: small logical commits with clear
  messages, pushed every week, matching your journal. A history that can't be followed costs
  points here, and may trigger a verification check.

## Experimental design and evaluation (4 points)

- **Controlled comparisons:** change one thing at a time, so you know what caused a difference.
- **Measurement:** use enough games to separate real differences from noise, and report
  intervals.
- **Ablations:** for the components of your final agent, show what each one contributes.
- **The journal:** this is where the evidence lives, entry by entry.

## Results analysis and limitations (4 points)

- **Why it works:** an explanation of why your agent plays the way it does, using game records
  and failure cases, not only ratings.
- **What failed:** what didn't work and why you think so.
- **The size trade-off:** how strength changed with model size in your experiments.

## Final report and recorded presentation (4 points)

- **Report:** at most 6 pages plus references, in the style of a workshop paper: problem,
  approach, experiments, results, limitations.
- **Recorded presentation:** about 5–8 minutes. Walk through what you built, how you evaluated
  it, and what did not work.

## Extra credit: top 10 of the final tournament

The top 10 entries by size-adjusted rating in the final tournament earn extra credit, in
percentage points added to the final course grade:

| Rank | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|---|---|---|---|---|---|---|---|---|---|---|
| Extra credit | 5.00 | 4.56 | 4.11 | 3.67 | 3.22 | 2.78 | 2.33 | 1.89 | 1.44 | 1.00 |

To receive it you must:

- follow every rule in [POLICIES.md](POLICIES.md);
- have training that reproduces when the staff retrain your entry;
- complete the live walkthrough.

If an entry is disqualified, the entries below it move up.
