# Rule: Creating an Architecture Decision Record (ADR)

## Goal

To capture significant architectural or design decisions in a lightweight, append-only format that survives longer than chat history and is more focused than a full PRD. ADRs document *why* a choice was made — the context, alternatives, and trade-offs. The *what* lives in the code itself.

ADRs are the long-term memory of a codebase. A future developer (possibly you, six months from now) reading the code will wonder "why is it this way?" — ADRs are the answer.

## When to Create an ADR

Create an ADR when:

- A PRD has multiple valid implementation approaches and one is chosen over the others
- A significant technology, library, or pattern decision is being made (e.g., Postgres over SQLite, REST over GraphQL, monorepo over polyrepo)
- A previous decision is being reversed or superseded
- A deliberate trade-off is being locked in that a future reader would need context to understand
- During task execution, you realize a non-obvious design choice is being made that isn't explained by the surrounding code

**Do NOT create an ADR for:**

- Trivial implementation details (variable naming, formatting, single-function refactors)
- Choices that are self-evident from the code
- Ephemeral or experimental decisions (use commit messages instead)
- Decisions already well-documented in an existing ADR — update the existing one's status if superseding

## Process

1. **Check for existing ADRs:** Scan `docs/adr/` for the highest existing ADR number and for any ADRs related to this decision. If a related ADR exists and the new decision supersedes it, note that relationship.
2. **Determine the next ADR number:** Use the next integer, zero-padded to 4 digits (e.g., `0008`). ADRs are append-only and numbered sequentially.
3. **Draft the ADR** using the structure below.
4. **Save:** `docs/adr/NNNN-short-kebab-title.md`. Create the `docs/adr/` directory if it doesn't exist.
5. **Cross-reference:**
   - If the ADR came out of a PRD, add a link to the PRD under the ADR's **Related** section.
   - Update the PRD's **Related Work** section to reference the new ADR.
   - If this ADR supersedes an older one, update the older ADR's **Status** line to `Superseded by ADR-NNNN` and link the new one.
6. **Commit on the current feature branch:** ADRs ride along with the PR that introduces the decision — they do not get their own PR.

## ADR Structure

````markdown
# ADR NNNN: [Short Decision Title]

## Status

[Proposed | Accepted | Deprecated | Superseded by ADR-XXXX]

## Context

What is the issue we're facing? What forces are at play (technical, political, organizational, project)? Describe the situation factually — no solutions yet. A future reader who has no context should be able to understand *why this decision needed to be made* from this section alone.

## Decision

What did we decide to do? State it plainly in the active voice: "We will X."

Keep this section short. The detail goes in Consequences and Alternatives.

## Consequences

What becomes easier as a result of this decision? What becomes harder? What new obligations does it create? What assumptions is it resting on that might not hold later?

Include both positive and negative consequences honestly. A section that only lists upsides is a suspect ADR.

## Alternatives Considered

- **[Alternative A]** — brief description and why not chosen
- **[Alternative B]** — brief description and why not chosen
- **Do nothing** — what happens if we don't make any change (always worth stating)

## Related

- PRD: `docs/features/[feature-name]-PLANNED/prd.md` (if this ADR stems from a PRD)
- Related ADRs: ADR-XXXX, ADR-YYYY
- Issue: #NN
- PR: #MM (filled in after the PR is opened)
````

## Status Lifecycle

- **Proposed** — drafted but not yet accepted (rare; most ADRs skip straight to Accepted when committed)
- **Accepted** — the decision is in effect
- **Deprecated** — the decision no longer applies, but nothing has replaced it
- **Superseded by ADR-XXXX** — explicitly replaced by a later ADR; link the replacement

**ADRs are append-only.** Never edit an old ADR's Decision or Context after it has been accepted. If the decision changes, write a new ADR that supersedes the old one and update the old one's Status line only. The historical record is the point.

## Target Audience

The reader is a future developer — possibly you — trying to understand why the codebase is the way it is. They have the current code but no context. They are not in the room. Write for them.

Avoid jargon that won't make sense out of context. Avoid "we decided to use X" without explaining why X was better than Y. Avoid omitting the alternatives — "we chose X" without "we rejected Y" is half an ADR.

## Final Instructions

1. Do NOT create an ADR for trivial decisions — prefer code comments or commit messages
2. Check `docs/adr/` for existing ADRs before writing a new one
3. Use the structure above verbatim
4. Cross-reference from the PRD (if applicable) and update any superseded ADRs' status lines
5. Commit on the current feature branch alongside the PRD and implementation — ADRs do not get their own PR
