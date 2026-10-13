# Resources

Everyone in the course has the same free tools available, so you don't need to pay for
anything to do well.

## AI assistants

You may use AI assistants and coding agents throughout the project. You must disclose your use
in `AI_USE.md` and follow the rules in [POLICIES.md](POLICIES.md#ai-assistants).

### Free to every ASU student

| Tool | Good for | How to get it |
|---|---|---|
| **ChatGPT Edu** (ASU workspace) | chat, writing and debugging code; includes Codex | Subscribe to "ChatGPT: User Account" in the [Self-Subscription Portal](https://asu.edu/selfsub), then sign in at <https://links.asu.edu/chatgpt-login> with your ASURITE ([details](https://ai.asu.edu/ai-tools/chatgpt-edu)). |
| **GitHub Copilot Student** | code completion and chat in VS Code and other editors | Get verified through GitHub Education, then turn the benefit on at <https://github.com/settings/education/benefits> ([details](https://docs.github.com/en/copilot/how-tos/manage-your-account/free-access-with-copilot-student)). |
| **CreateAI** (ASU's own platform: Chat, Builder, Compare) | dozens of models, including open models such as Qwen, in one place | <https://ai.asu.edu/createai-platform> |
| **Google Gemini** and **Microsoft Copilot Chat** (ASU accounts) | general chat | <https://ai.asu.edu/ai-tools/google-gemini>, <https://ai.asu.edu/ai-tools/copilot-chat> |

The full list of ASU-provided tools, with which ones students can use, is at
<https://ai.asu.edu/ai-tools>. Sign in with your ASU account, not a personal one, so ASU's data
protections apply. Never paste passwords, SSH keys or API keys into a chat.

### Other tools

You may use other assistants you have access to (personal subscriptions, other coding agents).
List them in `AI_USE.md` like everything else. Remember the play-time rule: an AI model may help
you **write** your agent, but it may not be **part of** your agent unless it is one of your own
networks inside the 250M-parameter limit.

## Sol

You train on ASU's Sol supercomputer using the **class account** set up for this course.

| What | Where |
|---|---|
| New to Sol: connecting, first steps | <https://docs.rc.asu.edu/new-user-guide> |
| Connecting (SSH and the web portal) | <https://docs.rc.asu.edu/connecting>, web portal <https://sol.asu.edu> |
| Submitting jobs with Slurm | <https://docs.rc.asu.edu/schedulers> |
| Class-account limits | <https://docs.rc.asu.edu/resource-limits> |
| Choosing the right account (`-A`) | <https://docs.rc.asu.edu/slurm-accounts> |
| Installed software and modules | <https://docs.rc.asu.edu/available-software> |
| Storage and file transfer | <https://docs.rc.asu.edu/storage> |
| Getting help from Research Computing | <https://docs.rc.asu.edu/contact-us> |
| Cluster status | <https://dashboard.sol.rc.asu.edu> |

**Class-account limits:**
- Submit with `-q class`.
- At most 2 jobs running and 10 in the queue at a time.
- At most 960 GPU-minutes of running time per person: for example 1 GPU for 16 hours, or 4 GPUs
  for 4 hours.
- Each job is limited to 32 CPU cores, 320 GB memory, 4 GPUs and 24 hours.
- If you also have a research account, pick the class one with `-A`.

**Good habits:**
- Run training and data generation as jobs, not on the login nodes.
- Request only the GPUs you will use. Data generation with Stockfish needs CPUs, not GPUs.
- Save checkpoints so a job that hits its time limit can resume.
- Write down the GPU-hours of every run in your journal.

The class also shares a course directory on Sol (`/data/courses/...`); its path and how to use it
will be announced on Canvas. Class accounts end with the course, so keep copies of anything you
want to keep.

## Learning the game

See the links in the [README](../README.md#6-learn-the-game). The best preparation is to play a few
games of Fog-of-War chess yourself.
