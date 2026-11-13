# Operating guide

This is how an agent actually runs the system. Read `ARCHITECTURE.md` first for the why. This file is the how: formats, rules and step-by-step procedures. Follow it exactly. If something here is unclear, ask Mark rather than inventing a convention.

## 1. Where things live

```
Agents/Threads/                      all saved threads (Drive only, not in the repo)
Agents/Threads/TAGS.md               tag registry: every tag name in use, one line each
Agents/Threads/<category>/           rough grouping, usually one per project or repo
                                     e.g. agent-voice-coding/
Agents/Threads/cross-cutting/        threads that don't fit one category
```

- Categories are **coarse and optional**. Tags do the real organizing. When in doubt, use `cross-cutting/`.
- Make a new category folder only for a new project or repo, and tell Mark when you do.

## 2. Thread document format

One thread is one Markdown file (`text/markdown`, **not** converted to a Google Doc, so the markers survive and stay searchable).

**Filename:** `YYYY-MM-DD_short-slug.md`, using the date the conversation started, e.g. `2026-11-13_thread-memory-architecture.md`.

**Front matter:**

```yaml
---
id: 2026-11-13_thread-memory-architecture
title: Thread-based memory architecture (from CTA)
started: 2026-11-13
source: claude.ai chat, voice + text
category: agent-voice-coding
continues: null            # id of an earlier thread this one picks up from, if any
tags: [cta-paper, thread-memory-architecture, contextual-retrieval]
---
```

`tags` lists every tag name used in the file, so a search for any of them finds the file.

**Body:** atoms in order, with range markers between them.

```
<range-start id="r1" tags="cta-paper">
<blurb>Mark asks whether the Conversation Tree Architecture paper (arXiv:2603.21278) can be built inside the Claude app; Claude summarizes the paper and proposes an artifact.</blurb>
</range-start>

<atom id="a001">
**Mark:** Is there a way to implement this here within the claude app? …
**Claude:** …
</atom>

<atom id="a002">
…
</atom>

<range-end id="r1"/>
```

## 3. Rules

**Atoms**
- An atom is one user message plus the reply to it. Number them `a001`, `a002`, and so on, in order.
- The text inside an atom is **immutable**: copy it verbatim and never edit it later. Voice transcription errors stay as they are, and a blurb can clarify them.
- Tool calls and results inside a turn are not copied verbatim. Summarize them in one bracketed line, e.g. `[searched Drive for Agents folder]`.

**Ranges (tags)**
- Ranges are **start and end markers**, not nested XML, so they can overlap freely.
- Markers go **only between atoms**, never inside one.
- Every range ends inside its own thread. Any range still open at the end gets its `range-end` before the end of the file. A topic that continues in another thread gets a new range there.
- A range can carry several tags: `tags="fruit-stand thread-memory-architecture"`.
- Range ids `r1`, `r2`, … are unique within the file.

**Blurbs**
- Write one blurb per range, inside its `range-start`.
- Keep it to 1–3 sentences (about 50–100 tokens), readable with no other context. Name the subject, what was decided or found, and how it relates to the thread's main topic.
- Blurbs are the main search surface, so use the words someone would search for.

**Tag names**
- Use lowercase-kebab-case.
- **Check `TAGS.md` before inventing a name.** Reuse an existing name if it fits.
- If you add a new name, append it to `TAGS.md` with a one-line definition.
- Prefer subject names (`fruit-stand`) over activity names (`brainstorming`).

**Continuity**
- Atoms in a file are implicitly linked in order. That link is the "came next, shared context" link and it is never changed.
- Set `continues:` when a thread deliberately picks up an earlier one.

## 4. Procedures

### A. Save a thread ("save this thread")

1. Get the full transcript: from the current context, or with the past-conversation tools if the thread is older.
2. Choose the category folder (§1).
3. Split it into atoms (§3). Copy verbatim.
4. Read the whole thread, then mark ranges where topics start and stop, including topics that drift away and come back (several ranges with the same tag are fine).
5. Write a blurb for each range.
6. Fill in the front matter, including `tags` and `continues`.
7. Check `TAGS.md`, then append any new names.
8. Upload the file. Tell Mark the path, the number of atoms and the tags used.

### B. Gather context for a new thread ("find everything about X")

1. Turn X into candidate tag names using `TAGS.md`, including related or synonymous ones.
2. Search `Agents/Threads/` for files whose text contains those names or the plain-language terms.
3. In each hit, read the `range-start` blurbs for the matching ranges first. Don't read whole files yet.
4. Pick the most relevant ranges. Prefer recent threads, decisions and conclusions over dead ends.
5. **Walk back** only where needed. If a range's atoms don't make sense alone, read earlier atoms in the same file, and follow `continues` to an earlier thread if necessary. Stop when the context is clear.
6. Produce a **context pack** for Mark to confirm:
   - pointers: `file → range id → atom ids`
   - a short synthesis of what is known about X
   - open questions or conflicts between threads
7. When the new thread is saved later, list the source threads in its first range's blurb, or set `continues` if it is a direct continuation.

### C. Retag an existing thread

- You may add, move or remove **markers and blurbs**, and update the front matter `tags`.
- Never change atom text.
- Drive files can't be edited in place: upload the corrected file with the same name, then trash the old one.

## 5. Things to avoid

- Don't split a thread into several files by topic. That is the tree model this system replaces.
- Don't paraphrase atoms.
- Don't invent near-duplicate tags (`fruitstand`, `fruit-stands`). Check the registry.
- Don't pull whole threads into context when blurbs and walk-back will do.
