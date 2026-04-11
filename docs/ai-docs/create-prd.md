# Rule: Generating a Product Requirements Document (PRD)

## Goal

To guide an AI assistant in creating a detailed Product Requirements Document (PRD) in Markdown format, based on an initial user prompt. The PRD should be clear, actionable, and suitable for a junior developer to understand and implement the feature.

## Process

1. **Receive Initial Prompt:** The user provides a brief description or request for a new feature or functionality. It could be a few lines, or a github issue.
2. **Get a perspective on the project** by reading details from README.md, CLAUDE.md, docs/, the last 5 PRs in github, and any logged github issues.
3. **Check for Related Work:** Scan `docs/features/` for existing PRDs and `docs/adr/` for existing ADRs that might overlap, duplicate, or extend the new request. If any are found, list them and confirm with the user whether this is a new feature, an extension, or a supersession before proceeding.
4. **Ask Clarifying Questions:** Before writing the PRD, the AI *must* ask clarifying questions to gather sufficient detail. The goal is to understand the "what" and "why" of the feature, not necessarily the "how" (which the developer will figure out).
5. **Generate PRD:** Based on the initial prompt and the user's answers to the clarifying questions, generate a PRD using the structure outlined below.
6. **Save PRD:** Create a new feature directory `docs/features/[feature-name]-PLANNED/` and save the generated document as `prd.md` inside that directory.
7. **Commit PRD on a feature branch:** If not already on a feature branch, create one: `git checkout -b feature/[feature-name]`. Never commit the PRD to `main`. Stage, commit, and push with `-u` to establish remote tracking.
8. **Create a single tracking issue:** Use `gh issue create` to open **one** tracking issue for the feature. Do NOT create multiple issues per PRD — a single tracking issue keeps traceability simple and matches the one-logical-change-per-PR workflow.
   - **Title:** the PRD title
   - **Body:** a one-paragraph summary, the repo-relative path to the PRD (`docs/features/[feature-name]-PLANNED/prd.md`), and the feature branch name
   - **Labels:** `feature` (or the repo's existing feature-tracking label)
9. **Link the issue back into the PRD:** Update the PRD's **Related Work** section with the issue URL and commit the update. Two commits on the feature branch is fine — the first establishes the PRD, the second closes the cross-reference loop.
10. **Flag architectural decisions for ADRs:** If the PRD process surfaced a significant architectural or design decision (choosing approach A over B, adopting a new dependency, picking a data store, etc.), ask the user whether to also create an ADR using `create-adr.md`. ADRs ride along in the same feature branch as the PRD.

## Status Management

The feature folder suffix tracks lifecycle state:

- **PLANNED**: Feature is documented but implementation has not begun
- **IN_PROGRESS**: Feature is being actively developed
- **COMPLETED**: Feature is fully implemented and merged

**State transitions are automated — the user never renames these folders manually:**

1. `create-prd.md` creates the folder at `-PLANNED`.
2. `process-task-list.md` promotes it to `-IN_PROGRESS` as the first step of task execution, when real work begins (code changes, not just planning).
3. The `close-the-loop` GitHub Action (`.github/workflows/close-the-loop.yml`) promotes it to `-COMPLETED` automatically when the feature's PR merges into `main` and the PR touched files outside `docs/features/`.

If you find a folder in a state that doesn't match the workflow phase (e.g., still `-PLANNED` after implementation has started), rename it by hand with `git mv` and commit — but the expected path is for the three automated steps above to handle everything.

## Clarifying Questions (Examples)

The AI should adapt its questions based on the prompt, but here are some common areas to explore:

*   **Problem/Goal:** "What problem does this feature solve for the user?" or "What is the main goal we want to achieve with this feature?"
*   **Target User:** "Who is the primary user of this feature?"
*   **Core Functionality:** "Can you describe the key actions a user should be able to perform with this feature?"
*   **User Stories:** "Could you provide a few user stories? (e.g., As a [type of user], I want to [perform an action] so that [benefit].)"
*   **Acceptance Criteria:** "How will we know when this feature is successfully implemented? What are the key success criteria?"
*   **Scope/Boundaries:** "Are there any specific things this feature *should not* do (non-goals)?"
*   **Data Requirements:** "What kind of data does this feature need to display or manipulate?"
*   **Design/UI:** "Are there any existing design mockups or UI guidelines to follow?" or "Can you describe the desired look and feel?"
*   **Edge Cases:** "Are there any potential edge cases or error conditions we should consider?"
*   **Platforms:** Will this be used on desktop, phone and tablet?

## PRD Structure Options

### Option 1: Standard PRD Structure

The generated PRD should include the following sections:

1.  **Introduction/Overview:** Briefly describe the feature and the problem it solves. State the goal.
2.  **Goals:** List the specific, measurable objectives for this feature.
3.  **User Stories:** Detail the user narratives describing feature usage and benefits.
4.  **Functional Requirements:** List the specific functionalities the feature must have. Use clear, concise language (e.g., "The system must allow users to upload a profile picture."). Number these requirements.
5.  **Non-Goals (Out of Scope):** Clearly state what this feature will *not* include to manage scope.
6.  **Design Considerations (Optional):** Link to mockups, describe UI/UX requirements, or mention relevant components/styles if applicable.
7.  **Technical Considerations (Optional):** Mention any known technical constraints, dependencies, or suggestions (e.g., "Should integrate with the existing Auth module").
8.  **Success Metrics:** How will the success of this feature be measured? (e.g., "Increase user engagement by 10%", "Reduce support tickets related to X").
9.  **Open Questions:** List any remaining questions or areas needing further clarification.
10. **Related Work:** Links to the tracking GitHub issue, related PRDs in `docs/features/`, and related ADRs in `docs/adr/`. Start as a placeholder during drafting; fill in after the tracking issue is created.

### Option 2: Comprehensive Engineering PRD Structure

For complex technical features or when requested by the user, use this more detailed structure:

1.  **Overview:** Brief feature description and problem it solves
2.  **Problem Statement:** Detailed context and justification
3.  **Goals:** Organized into Primary and Secondary goals
4.  **Success Criteria:** Specific, measurable checkboxes for validation
5.  **Requirements:** Subdivided into:
    - **Functional Requirements** (numbered, specific features)
    - **Technical Requirements** (numbered, system/environment needs)
    - **Non-Functional Requirements** (numbered, performance/security/maintainability)
6.  **User Stories:** Organized by persona/role
7.  **Technical Specifications:** Include code examples, configurations, API specs
8.  **Dependencies:** Split into External and Internal dependencies
9.  **Timeline:** Phased approach with estimated timeframes
10. **Risks and Mitigation:** Risk/mitigation strategy pairs
11. **Out of Scope:** Clear exclusions and boundaries
12. **Acceptance Criteria:** Grouped validation criteria
13. **Related Work:** Links to the tracking GitHub issue, related PRDs in `docs/features/`, and related ADRs in `docs/adr/`. Start as a placeholder during drafting; fill in after the tracking issue is created.

### When to Use Each Structure

- **Use Option 1** for simple features, UI changes, or when working with product managers
- **Use Option 2** for complex technical features, integrations, infrastructure changes, or when the user requests "comprehensive" or "detailed" PRDs
- **Ask the user** which structure they prefer if unclear from the prompt

## Target Audience

Assume the primary reader of the PRD is a **junior developer**. Therefore, requirements should be explicit, unambiguous, and avoid jargon where possible. Provide enough detail for them to understand the feature's purpose and core logic.

## Output
*   **Format:** Markdown (`.md`)
*   **Location:** `docs/features/[feature-name]-PLANNED/`
*   **Filename:** `[feature-name]-prd.md`

## Clarification Questions Output Format

After gathering context and before asking clarifying questions, output all questions to the terminal in this structured format:

```
=== PRD CLARIFICATION QUESTIONS ===

Question 1: [Question text]
     1.1: [Option 1]
     1.2: [Option 2]
     1.3: [Option 3]
     ...
     1.N: [Option N]
     1.X: Something else

Question 2: [Question text]
     2.1: [Option 1]
     2.2: [Option 2]
     2.3: [Option 3]
     ...
     2.N: [Option N]
     2.X: Something else

...

Question N: [Question text]
     N.1: [Option 1]
     N.2: [Option 2]
     N.3: [Option 3]
     ...
     N.N: [Option N]
     N.X: Something else

===================================
```

**Guidelines:**
- Each question should have 2-5 specific options plus the "X: Something else" option
- Options should be actionable and specific to the feature context
- The "X: Something else" option always allows for custom input
- Number questions sequentially (1, 2, 3, ...)
- Number options within each question (1.1, 1.2, etc.)
- Use this format before engaging in the conversational Q&A with the user

**Example:**

```
=== PRD CLARIFICATION QUESTIONS ===

Question 1: What is the primary goal of this user authentication feature?
     1.1: Allow new users to create accounts
     1.2: Enable existing users to log in securely
     1.3: Support social login (Google, GitHub, etc.)
     1.4: Implement password reset functionality
     1.X: Something else

Question 2: Which authentication method should be prioritized?
     2.1: Email and password
     2.2: OAuth (social login)
     2.3: Magic link (passwordless)
     2.4: Multi-factor authentication (MFA)
     2.X: Something else

Question 3: What platforms need to support this feature?
     3.1: Web only (desktop)
     3.2: Web (desktop + mobile responsive)
     3.3: Native mobile apps (iOS/Android)
     3.4: All platforms
     3.X: Something else

===================================
```

## Final instructions
1. Do NOT start implementing the PRD
2. Output clarifying questions using the structured format above
3. Make sure to ask the user clarifying questions
4. Take the user's answers to the clarifying questions and improve the PRD
5. Commit the PRD on a feature branch (never `main`) and push with `-u`
6. Create a single GitHub tracking issue with `gh issue create` and link it in the PRD's Related Work section
7. If the PRD involved a significant architectural decision, prompt the user to create an ADR using `create-adr.md`
8. Ask the user if they want to break the PRD down into dev tasks using `generate-tasks.md` (Reply "yes" or "y" to continue)
