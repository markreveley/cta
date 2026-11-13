# CTA design notes

## Data model

Each person's trees are stored privately in the artifact's database:

```
data/users/<uid>/profile/trees/<treeId>              tree doc
data/users/<uid>/profile/trees/<treeId>/nodes/<id>   one doc per node
```

**Tree**

```json
{ "id": "…", "title": "…", "links": [{ "from": "nodeA", "to": "nodeB", "ts": 0 }],
  "lastActive": "nodeId", "createdAt": 0, "updatedAt": 0 }
```

`links` records cross-node passes so they can be drawn. Parent–child edges come from `parentId`.

**Node**

```json
{ "id": "…", "parentId": "… | null", "title": "…", "volatile": false,
  "inherited": { "mode": "full | summary | selected", "text": "…" },
  "messages": [
    { "id": "…", "role": "user | assistant", "content": "…", "ts": 0 },
    { "id": "…", "role": "context", "kind": "merge | cross", "from": "<node title>", "content": "…", "ts": 0 }
  ],
  "merges": 0, "createdAt": 0 }
```

Storing one document per node keeps each write small and stays under the store's 256 KiB-per-document limit. If the database isn't available, for example when the page runs outside Claude, the same interface falls back to `localStorage`.

## Prompt construction (context isolation)

At inference time the active node's prompt contains only the following:

1. A short preamble. It says Claude is answering inside one node of a tree, gives the node's title and volatile flag, and wraps any inherited context in `<inherited_context mode="…">`.
2. The node's own messages, in order. `context` messages become user-turn `<note source="merged branch: X">…</note>` blocks.
3. Consecutive same-role turns are joined so that the roles alternate.

No other node's content is ever included. That rule is the whole isolation guarantee.

## The paper's open questions, and the answers here

The paper leaves the selection, compression and merge functions open, and its prototype merges by hand. This implementation makes the following choices:

| Question | Choice here |
|---|---|
| What gets passed down? | The user chooses: full copy, a Claude summary (bullets, under 200 words), hand-picked messages, or nothing. |
| How condensed is a merge? | Claude drafts a note of conclusions, decisions and facts (under 150 words) and is told to skip dead ends and anything already inherited. The user always edits it before it's committed. A verbatim "selected messages" path also exists. |
| Where does merged content go? | Merged content is appended to the end of the parent's window, in chronological order, as a labeled note. The parent's earlier turns are left unchanged. |
| Deleting a node that has children? | Blocked. Children must be closed first, which keeps merges local and easy to follow. |
| Volatile vs. normal close | Closing either kind offers merge or purge. Volatile nodes are dashed in the tree and labeled as exploratory in their preamble. |

## Possible next steps

- **Evaluation**, which the paper lists as future work. Have Claude grade answers from the same question asked in a CTA node and in a flat transcript, and log token counts per node against a flat baseline.
- **Relevance filtering.** Claude would suggest which parent messages to carry into a branch and pre-tick them in the "Selected" picker.
- **Subtree merges.** Close a node together with all its descendants, merging bottom-up.
- **Multi-agent nodes** (from the paper's extensions). Give each node its own role prompt.
- **Export and import** of a tree as JSON. Markdown export exists already.
