# Working on this project

Read `README.md`, then `ARCHITECTURE.md`, then `GUIDE.md`, before you do anything.

## Where things live

| Place | Holds | Role |
|---|---|---|
| GitHub `markreveley/cta` | **Everything**: docs, plus any code and tests | Source of truth for the project itself |
| Google Drive `Agents/cta/` | **Everything except code** (same paths as the repo) | Cached copy for reading and planning |
| Google Drive `Agents/Threads/` | Saved conversation threads, in category folders, plus `TAGS.md` | The system's data. **Drive only, not in the repo.** |

Code is an implementation detail. The Drive copy describes what the system is and how to operate it, but not how it's coded.

## Rules

1. Project docs change in the **repo first**. Then refresh the Drive copy at the same path.
2. No code (`.html`, `.js`, `.py` and so on) in `Agents/cta/`.
3. Never edit the Drive copy on its own. If Drive is newer, copy it back into the repo first.
4. Threads follow `GUIDE.md` exactly. Check `Agents/Threads/TAGS.md` before using any tag.
5. The CTA prototype (`examples/cta-poc/`) is reference only. Don't extend it.
