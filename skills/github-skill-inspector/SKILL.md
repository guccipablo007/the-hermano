# GitHub Skill Inspector

## Purpose

Use this skill when the user gives Hermes a GitHub link for a skill, tool, script, repository, or plugin.

Hermes should inspect the link, understand what it does, identify risks, and present it to Your Majesty for validation before installation unless the user explicitly already authorized installation.

## When To Use

Use when the user says things like:

- install this skill
- use this GitHub skill
- here is a GitHub link
- can Hermes use this repo?
- add this tool to Hermes
- research this skill

## Steps

1. Identify the GitHub URL.
2. Inspect repository name, README, install instructions, dependencies, and scripts.
3. Look for:
   - shell scripts
   - network access
   - credential handling
   - destructive commands
   - suspicious code
   - required API keys
4. Summarize what the skill/tool does.
5. Explain benefits for Your Majesty.
6. Explain risks.
7. Recommend:
   - install
   - do not install
   - inspect further
8. Ask for validation before installing if external/untrusted.
9. If approved, install safely:
   - backup relevant config
   - validate syntax/config
   - test in isolation
   - report exact result

## Safety

Do not run unknown install scripts blindly.
Do not expose secrets.
Do not install tools that request private data without clear reason.
Do not modify Gmail/YouTube/token systems without explicit approval.
