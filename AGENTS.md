# Working on this repo

Read this before changing anything in CTA, whether you're a person or an agent.

## Where things live

| Place | Holds | Role |
|---|---|---|
| GitHub: `markreveley/cta` | **Everything**: code, tests and docs | Source of truth |
| Google Drive: `Agents/cta/` | **Everything except code**: all docs, in the same folders as the repo | Cached copy for reading and planning |
| Claude artifact "Conversation Tree" | The published `index.html` | Running app |

The code (`index.html`, `tests/`) is an implementation detail. The Drive copy describes *what* CTA is and *why*, but not how it's coded.

## Rules

1. **Change the repo first.** Then refresh the Drive copy of any non-code file you touched, using the same path relative to `Agents/cta/`.
2. **Don't put code in Drive.** That means `.html`, `.js`, `.py` and other source files. Markdown and other docs go there.
3. **Never edit the Drive copy on its own.** If you find a newer version in Drive, copy it back into the repo first.
4. **Republish the artifact** after `index.html` changes. It needs the capabilities `sample`, `db` and `user`.
5. **Run the smoke test** before publishing: `python3 tests/smoke_test.py`.

## Layout

```
README.md          overview and paper mapping        (Drive copy)
AGENTS.md          this file                         (Drive copy)
docs/DESIGN.md     data model, prompts, open issues  (Drive copy)
index.html         the whole app                     (repo only)
tests/smoke_test.py  UI flow and isolation checks    (repo only)
```
