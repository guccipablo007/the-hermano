# Hermes Self-Improvement Skill

## Purpose

Use this skill when Hermes completes a new task type successfully and the workflow is likely to be repeated.

Hermes should turn useful successful workflows into reusable skills.

## When To Use

Use after successful completion of tasks such as:
- creating a new file workflow
- building a webapp
- generating a repeated content format
- creating YouTube Shorts SEO packages
- creating kids worksheets or flashcards
- integrating an API
- solving a VPS/Hermes setup issue
- installing and testing a GitHub skill
- creating a repeatable research/report workflow

Do not use for tiny one-off tasks.

## How To Create A Skill

1. Identify the reusable workflow.
2. Give the skill a clear lowercase folder name.
3. Create a `SKILL.md` file.
4. Include:
   - purpose
   - when to use
   - required inputs
   - output format
   - step-by-step process
   - safety notes
   - example user requests
5. Keep the skill practical.
6. Do not include secrets, passwords, API keys, or OAuth tokens.
7. If the workflow touches Gmail or YouTube analytics, mark it as sensitive and require controlled handling.

## Skill Folder Location

Skills should live under:

`/root/.hermes/skills/<skill-name>/SKILL.md`

## Example Skill Structure

```markdown
# Skill Name

## Purpose
What this skill helps Hermes do.

## When To Use
Types of user requests that should trigger this skill.

## Inputs
What information is needed.

## Steps
1. Step one.
2. Step two.
3. Step three.

## Output
What Hermes should produce.

## Safety
Sensitive data, confirmations, or restrictions.

## Examples
- Example user request.
```

## Safety

Never save secrets into skills.
Never save Gmail private content into skills.
Never save YouTube private analytics data into skills.
Save only reusable process knowledge.
