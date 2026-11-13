# CTA (working name): thread-based memory

**What this project is:** a system where every conversation is saved as an immutable **thread**, split into **atoms** (single exchanges), with overlapping **tag ranges** laid over it. Tags connect subjects across threads, so an agent can gather the right context to start a new thread ("find everything about X") and trace any past exchange back to exactly the context it had.

The name "CTA" comes from the paper that started this: *Conversation Tree Architecture* (arXiv:2603.21278). **We are not implementing CTA.** Its tree model files content by where you were standing rather than by what you discussed, so drifting topics end up orphaned in the wrong branch. This system replaces branching with tagging. See `ARCHITECTURE.md` for the reasoning.

## Read in this order

1. `README.md`: this file.
2. `ARCHITECTURE.md`: the model (threads, atoms, tag ranges, links, blurbs, retrieval) and its open questions.
3. `GUIDE.md`: the operating manual: file format, tag rules, and the procedures for saving threads and gathering context. **An agent doing the work follows this.**
4. `AGENTS.md`: where things live (repo vs. Drive) and the current sync status.

## Where the data lives

- Saved threads: Google Drive `Agents/Threads/`, organized as described in `GUIDE.md`.
- Tag registry: `Agents/Threads/TAGS.md`.

## Set aside

- `examples/cta-poc/` holds the docs for a working prototype of the original CTA paper: a Claude artifact app with tree view, branching and merging. It is kept **for reference only** and is not being developed further.

## Status

Design stage. The architecture is drafted, the operating guide is written, and the first thread is saved as a worked example: `Agents/Threads/cta/2026-11-13_cta-to-thread-memory.md` (28 atoms, 12 tag ranges). Nothing is automated yet: an agent saves and retrieves threads when asked.
