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

## Summary hierarchy (coarse to fine)

Search reads summaries from the top down and only opens finer levels where the coarser one matches:

| Level | Unit | Summary | Written |
|---|---|---|---|
| 1 | Thread | `summary` in the front matter: 2–4 sentences covering the whole thread | When the thread is saved; rewritten if ranges change a lot |
| 2 | Tag range | Range blurb | When the range is marked |
| 3 | Atom | None; the verbatim text | Never changes |

The thread summary lets a search drop whole threads before reading any range blurbs. That matters once there are hundreds of thread files.

This mirrors **Zyphra Hierarchical Attention** (ZHA, arXiv:2610.42112), which applies the same idea inside a model. It builds a tree of compressed summaries over the KV cache, and each query descends it from coarse to fine instead of scoring every token. ZHA reports that the set of tokens a query really needs grows as a sublinear power law with context length. That is evidence for summary-first retrieval over loading whole histories. ZHA also summarizes each chunk from several learned angles ("reference queries"), so one average doesn't drown out a minority signal. Overlapping tags on a range play the same role here.

ZHA does not replace this system, even if models with cheap, huge context windows arrive. Attention picks tokens implicitly and leaves no record. This system keeps explicit, curated pointers, so you can always see where context came from.

## Retrieval flow (sketch)

1. A new thread starts with a request such as: "gather context on fruit-stand, then focus on X".
2. The agent matches tag names and reads thread summaries to shortlist threads, then reads range blurbs within those threads to collect candidate ranges.
3. The agent picks the most relevant ranges and atoms (relevance filtering).
4. For each pick it walks `prev` within that thread until the context is clear, and follows a thread-continuation link when one exists.
5. The selections become the new thread's starting context, recorded as pointers rather than copies, so you can always trace where the context came from.

## Relationship to CTA

- A CTA "box" is just one **view**: a single tag range rendered on its own.
- CTA's downstream pass becomes "start a thread from selected ranges". Its upstream merge becomes "tag and blurb the range".
- The existing CTA artifact (repo `markreveley/cta`) stays as a working prototype of the tree view.

## Related work: UniiChat

[UniiChat](https://github.com/VictorTaelin/uniichat) (Victor Taelin / Higher Order Company, Apache-2.0, last commit 2026-10-19) is the closest existing system. It's an agent with **one chat that never ends**.

- **Structure.** Every message is logged unchanged, as append-only JSON lines. A cheaper "compactor" model summarizes each message into one line, then merges adjacent lines in pairs into a **binary tree**.
- **View.** Each call sees the whole chat in up to 128 KB. Recent messages get one line each, and older stretches are covered by fewer, broader nodes. Detail fades with age, but nothing is deleted.
- **Zoom.** The agent opens any node into its two children, down to the original message. Its prompt makes zoom the *only* allowed way to navigate memory: no searching.
- **Practicalities.** The tree builds in the background, and the view changes only at its end, so most input is served from the prompt cache. It also imports past Claude and ChatGPT chats.
- **Caveat.** The README says the code is vibe-coded: written and reviewed by AI agents, so expect bugs. Treat it as a reference design.

**Where it matches this design:** an immutable raw log (our atoms), coarse-to-fine summaries with drill-down to the original text (our blurbs and walk-back), and summaries written once and kept.

**Where it's stronger:**
- It manages the **live** context window automatically. That's our gap: a thread here is one flat window, and saving is manual.
- It runs: real code with tools, subagents, prompt caching and imports.

**Where this design is stronger:**
- **Topical recall.** UniiChat merges by position, so a topic that returns months later is reachable only by zooming down from summaries that may have dropped it. Tags here find a topic at any age, in one lookup.
- **Overlapping topics.** A pair merge can straddle a topic change, and one summary line can't hold two topics fairly. Overlapping ranges can.
- **Curation and provenance.** Here, what gets pulled in is visible and editable, rather than fading on a fixed schedule.
- **Cost.** One blurb per range, against roughly 2N summary calls for N messages.

| | UniiChat | This design |
|---|---|---|
| Unit of history | One endless chat | Many threads |
| Hierarchy built by | Position (adjacent pairs) | Topic (tag ranges at topic shifts) |
| Finding old material | Zoom down from the top only | Tag lookup, then blurbs, then walk-back |
| Live window | Managed automatically | Not managed (open question) |
| Writing summaries | Every message and merge, automatic | Range blurbs and thread summary, at save |

## Open questions

- Who writes tags: the user, the agent as it goes, or the agent in a pass afterwards?
- What is the tag vocabulary: free text, a controlled list, or names merged over time?
- How does the agent decide it has walked back far enough?
- Where are things stored (threads, atoms, ranges, blurbs), and how are they indexed (keyword, embeddings, both)?
- How does this relate to Elixir Mind and the earlier `thread-based-dag` and `personal-DAG` work?
- **Should we combine with UniiChat's approach?** The idea is to use a UniiChat-style positional binary tree *inside* each thread, to run the live context window and to produce the thread summary (the tree's root). Tags would work *across* threads, as a topical index into atoms. Time is handled by the tree and subject by the tags. Still to work out:
  - Do tree nodes and tag ranges need to line up, for example a range starting a new subtree?
  - Is per-message summarization worth its cost when range blurbs already exist?
  - With one endless chat, is a "thread" still a useful boundary, or do ranges become the only unit? Ranges are closed at thread ends today.
