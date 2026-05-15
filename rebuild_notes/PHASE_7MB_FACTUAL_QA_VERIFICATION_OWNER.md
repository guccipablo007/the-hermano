# Phase 7M-B: Factual Q&A Verification Owner

Date: 2026-05-16

## Goal

Add one factual Q&A owner without changing provider/model routing, reminder logic, artifact logic, `/btw`, or delegated-action safety policy.

## Live Files

- `/root/.hermes/scripts/hermes_verified_fact.py`
- `/root/.hermes/scripts/hermes_live_natural_router.py`
- `/root/.hermes/skills/factual-qa/SKILL.md`
- `/root/.hermes/rebuild_notes/PHASE_7MB_FACTUAL_QA_VERIFICATION_OWNER.md`

## Ownership Decision

Canonical factual Q&A ownership now sits in `hermes_live_natural_router.py` for matching factual questions.

The router sends those questions to:

- `hermes_verified_fact.py`

This keeps Phase 7M-A intact:

- one canonical Telegram router
- no legacy `/btw` pre-router
- no legacy reminder lookup pre-router
- no legacy artifact pre-router
- shared final sanitizer still handled by the gateway

## Initial Fact Profiles

- electric airplane / electric air plane / electric aircraft
- electric car
- capital of France

## Verification Strategy

- direct known fact or distinction for low-risk canonical facts
- verified web-page checks for electric airplane and electric car source records
- concise `NOT VERIFIED` for current, high-stakes, or unmatched source-sensitive questions

## Expected Electric-Airplane Distinction

- Any electric aircraft: Albert and Gaston Tissandier, electric airship, 1883
- Crewed heavier-than-air electric airplane: MB-E1, 1973, Fred Militky and the Brditschka aircraft team in Austria

## Non-Goals

- no factual-model rewrite
- no provider/model changes
- no reminder wording cleanup
- no news retriever changes
- no artifact verification changes
