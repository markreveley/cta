# CTA: Conversation Tree Architecture, inside Claude

This app implements *Conversation Tree Architecture: A Structured Framework for Context-Aware Multi-Branch LLM Conversations* (Hemanth & Saha, arXiv:2603.21278). It runs as a Claude artifact.

A normal chat is one append-only context window, so topics bleed into each other. The paper calls this *logical context poisoning*. CTA instead organizes a conversation as a **tree of context-isolated nodes**. Each node answers from its own window, and information moves between nodes only through explicit operations.

## What it does

| Paper concept | In the app |
|---|---|
| Context-isolated node | Each node sends Claude only its own window: what it inherited, its own messages, and any notes merged or passed into it. |
| Downstream passing | **Branch** lets you start a child with one of four contexts: *Full context*, *Summary* (Claude condenses the parent), *Selected messages*, or *Clean slate*. |
| Upstream merging | **Close branch → Merge up** has Claude draft a merge note. You edit it, and it's appended to the parent as a marked note. You can also merge selected messages verbatim. |
| Cross-node passing | **Send to node…** copies a summary, the latest reply, or your own text into any other node, such as a sibling. It's drawn as a dashed orange edge. |
| Volatile nodes | **Explore (volatile)** creates a temporary branch. Closing it forces a choice: merge or purge. |
| Tree visualization | A tappable SVG tree shows branch edges, cross-node edges, ↑n merge badges, volatile outlines, and an approximate token count per node. |

Each node also shows roughly how many tokens are in its window, which makes the paper's token-efficiency argument visible.

## Running it

- **As a Claude artifact (intended).** Publish `index.html` as an artifact and declare the capabilities `sample` (calls Claude), `db` and `user` (stores each person's trees privately under `data/users/<id>/`). It works in the Claude web, desktop and mobile apps.
- **Standalone.** Opening `index.html` directly in a browser renders the UI and keeps trees in `localStorage`. Sending messages needs the Claude runtime, which is absent there, and the page says so.

## Files

- `index.html` is the whole app: one self-contained file with no build step.
- `docs/DESIGN.md` covers the data model, prompt construction, and the open questions from the paper and how this implementation answers them.

## Status

This is a working prototype. As with the paper, nothing has been evaluated empirically. Ideas for evaluation are in `docs/DESIGN.md`.
