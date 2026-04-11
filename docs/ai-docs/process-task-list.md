# Task List Management

Guidelines for managing task lists in markdown files to track progress on completing a PRD

## Starting Execution

Before implementing any sub-task, promote the feature folder from `-PLANNED` to `-IN_PROGRESS`. This is the point in the workflow where planning ends and work begins — the folder name must reflect that.

1. **Locate the parent feature folder.** It is the directory containing `tasks.md` (e.g., `docs/features/user-auth-PLANNED/`).
2. **If the folder is named `*-PLANNED`:**
   - `git mv docs/features/[feature-name]-PLANNED docs/features/[feature-name]-IN_PROGRESS`
   - If `status.md` exists inside, update it:
     - Replace `Implementation Status: PLANNED` with `Implementation Status: IN_PROGRESS`
     - Replace `📋 PLANNED` with `🚧 IN_PROGRESS` in the title line
     - Update `**Last Updated:**` to today's date
   - Commit on the current feature branch with subject `chore: start work on [feature-name]`.
3. **If the folder is already `*-IN_PROGRESS`:** proceed directly — the rename was done on a prior run.
4. **If the folder is `*-COMPLETED`:** stop and confirm with the user. You should not be executing a task list against a completed feature.

This transition happens exactly once per feature, at the start of implementation. The `-IN_PROGRESS` → `-COMPLETED` transition is handled automatically by the `close-the-loop` GitHub Action when the feature's PR merges into `main` — do not attempt it manually here.

## Task Implementation
- Start a new gh branch
- **One sub-task at a time:** Do **NOT** start the next sub‑task until you ask the user for permission and they say “yes” or "y"
- **Completion protocol:**
  1. When you finish a **sub‑task**, immediately mark it as completed by changing `[ ]` to `[x]`.
  2. If **all** subtasks underneath a parent task are now `[x]`, also mark the **parent task** as completed.
- Stop after each sub‑task and wait for the user’s go‑ahead.

## Task List Maintenance

1. **Update the task list as you work:**
   - Mark tasks and subtasks as completed (`[x]`) per the protocol above.
   - Add new tasks as they emerge.

2. **Maintain the “Relevant Files” section:**
   - List every file created or modified.
   - Give each file a one‑line description of its purpose.

## AI Instructions

When working with task lists, the AI must:

1. Regularly update the task list file after finishing any significant work.
2. Follow the completion protocol:
   - Mark each finished **sub‑task** `[x]`.
   - Mark the **parent task** `[x]` once **all** its subtasks are `[x]`.
3. Add newly discovered tasks.
4. Keep “Relevant Files” accurate and up to date.
5. Before starting work, check which sub‑task is next.
6. After implementing a sub‑task, update the file.
7. Pause for user approval to commit to gh. (Reply “yes” or “y” to continue)
8. Commit code to git.

## Architectural Decisions During Execution

If while executing a sub-task you realize a significant architectural or design decision is being made that isn't explained by the PRD or existing code (e.g., choosing a library, locking in a data model, picking between two valid approaches), **pause and create an ADR using `create-adr.md` before committing the implementation**. The ADR rides along in the same feature branch as the code change. This prevents undocumented decisions from accreting silently as you work through the task list.
