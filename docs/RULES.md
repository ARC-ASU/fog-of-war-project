# Game rules

Fog-of-War chess (also called Dark Chess) is chess in which you cannot see most of your
opponent's pieces. The reference implementation is [`fow/game.py`](../fow/game.py). If this
page and the code ever disagree, the code decides official games; please report the mismatch.

## Moves

All pieces move as in standard chess, including pawn double steps, en passant, promotion and
castling, with these differences:

1. **There is no check.** You may move into check, stay in check, or leave your king attacked.
   Nothing warns you.
2. **You win by capturing the opponent's king.** There is no checkmate or stalemate.
3. **Castling** requires only the castling right (king and that rook have not moved) and empty
   squares between king and rook. It is allowed even if the king is attacked, passes through
   an attacked square, or lands on one.

## What you see

On your turn you see:

- all of your own pieces;
- every square that one of your legal moves lands on, and any enemy piece standing there;
- for an en-passant capture, also the pawn it would remove.

Nothing else. In particular, a square your pawn could capture onto is visible only if there is
an enemy piece on it to capture. A square straight in front of your pawn is visible only if it is
empty, since the pawn can move there only then.

You are also told the move you played last and, if the opponent captured one of your pieces on
their last move, the square where it happened. You are not told what the opponent moved.

## End of the game

| Result | When |
|---|---|
| Win | You capture the opponent's king. |
| Loss | Your king is captured, or you forfeit: an illegal move, an exception, a crash, or running out of time. |
| Draw | The side to move has no legal move; or 100 plies in a row pass without a capture or pawn move; or the game reaches 400 plies. |

There is no threefold-repetition rule and no draw by agreement.

## Example

After 1. e4, Black sees its own pieces, the squares its pieces could move to (ranks 6 and 5
for the pawns, a6/c6/f6/h6 for the knights), and nothing of White's: no black move lands on a
white piece yet. White's pawn on e4 is invisible to Black.
