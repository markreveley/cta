# CTA: Architecture (working draft)

Status: design draft from a voice discussion on 2026-11-13. Name kept as "CTA" for now. It was inspired by the Conversation Tree Architecture paper (arXiv:2603.21278) but moves away from the tree model.

## Goal

One structure that works as conversation history, memory system and knowledge graph at the same time:

- conversations stay intact, in the order they happened;
- topics can be found and reused across conversations;
- for any past exchange, you can rebuild exactly what context was in play when it happened.

## Why not a tree

CTA splits topics up front, when you branch, and gives each node exactly one parent. Real conversations drift and mix topics, so a stretch that is about two things has to pick a side. This design keeps the conversation whole and lays topic structure over it afterwards.

## Core entities

### Thread (source of truth)

- An ordered, immutable sequence of exchanges that shared one context window.
- It has a first-class rendering as a single document: the full transcript with tag markers inline.
- It is self-contained. Nothing inside a thread points into another thread's internals.

### Atom (exchange)

- One question/response turn inside a thread.
- Derived from the thread, which "explodes" into its atoms.
- Linked to the previous atom by an immutable `next`/`prev` link (a linked list). This link exists because context was shared, so it is a fact, not an association.
- Walking `prev` from any atom rebuilds exactly the context the model had at that turn. This works the same way as walking git history.

### Tag range

- A named range over a thread, with a start marker and an end marker (for example `<tag name="fruit-stand">…</tag>`).
- Ranges may **overlap**: one stretch can be both `fruit-stand` and `knowledge-graph`. This replaces CTA's single-parent branching.
- Ranges are **bounded by their thread**. Every open range closes at the end of the thread at the latest. A topic that continues in a later thread starts a new range there.
- Tags can be added, fixed or removed later without touching the thread, because the thread itself never changes.

### Tag name (cross-thread link)

- The **name** is what connects threads, not the range. "fruit-stand" in thread A and "fruit-stand" in thread B are separate ranges that share a name.
- The set of names is the knowledge graph's vocabulary.

## Inheritance

- An atom inherits every tag whose range contains it, so a single exchange can carry several tags.
- Tags are written at range level and resolved per atom by position.

## Two kinds of links

| Link | Between | Mutability | Meaning |
|---|---|---|---|
| Continuity (`prev`/`next`) | atoms in one thread | immutable | "came next; shared context" |
| Association (tag name) | ranges in any threads | ephemeral / editable | "about the same subject" |
| Thread continuation (optional) | thread → earlier thread | set once | "picked up where that one left off", so a walk back can cross threads |

## Context and blurbs

The problem: a single atom is too thin to use on its own ("but where would the bananas come from?").

Options discussed:

1. **Blurb per atom** (contextual retrieval: prepend 50–100 tokens of situating context before indexing). Good for retrieval, but costly when written for every turn.
2. **Lazy walk-back.** No precomputed context. At use time the agent follows `prev` links until it judges it has enough. It is accurate and free up front, but you pay on every reuse, and "enough" is a judgment call.
3. **Chosen direction: strategic blurbs plus walk-back.**
   - A blurb is written **at the start of each tag range**, the point where CTA would have branched into a new box.
   - **Finding** is handled by tag names and range blurbs.
   - **Understanding** is handled by walking back from the found atom, with the range blurb as a shortcut.

## Retrieval flow (sketch)

1. A new thread starts with a request such as: "gather context on fruit-stand, then focus on X".
2. The agent matches tag names and searches range blurbs, then collects candidate ranges from all threads.
3. The agent picks the most relevant ranges and atoms (relevance filtering).
4. For each pick it walks `prev` within that thread until the context is clear, and follows a thread-continuation link when one exists.
5. The selections become the new thread's starting context, recorded as pointers rather than copies, so you can always trace where the context came from.

## Relationship to CTA

- A CTA "box" is just one **view**: a single tag range rendered on its own.
- CTA's downstream pass becomes "start a thread from selected ranges". Its upstream merge becomes "tag and blurb the range".
- The existing CTA artifact (repo `markreveley/cta`) stays as a working prototype of the tree view.

## Open questions

- Who writes tags: the user, the agent as it goes, or the agent in a pass afterwards?
- What is the tag vocabulary: free text, a controlled list, or names merged over time?
- How does the agent decide it has walked back far enough?
- Where are things stored (threads, atoms, ranges, blurbs), and how are they indexed (keyword, embeddings, both)?
- How does this relate to Elixir Mind and the earlier `thread-based-dag` and `personal-DAG` work?
