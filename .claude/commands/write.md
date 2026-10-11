---
description: Run the funnel for a section: beats -> bank -> patterns -> draft, stopping for Joe after each stage
argument-hint: <section>
---
Run the stages for $ARGUMENTS in order using the commands /beats, /bank, /patterns, /draft (see their files). STOP after each stage and wait for Joe's approval/picks before the next. Never loop on tool checks, never overwrite Joe's lines, no unbounded agents (CLAUDE.md principle 8). After /draft, offer /polish then /review then /lock.
