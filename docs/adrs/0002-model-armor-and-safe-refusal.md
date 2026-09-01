# ADR 0002: Defense-in-Depth AI Safety via GCP Model Armor and Scope Lock Engine

## Status
Accepted

## Context
Deploying AI in healthcare environments introduces severe safety and liability risks:
1. **Adversarial Exploitation**: Prompt injection or jailbreak attempts attempting to bypass safeguards.
2. **Unauthorized Medical Advice**: Users asking for medical diagnosis, prescriptions, or treatment plans ("Should I take 50mg of drug X?").
3. **PII / PHI Leakage**: Users submitting sensitive patient identifiers.

## Decision
We implement a dual-layer, defense-in-depth safety architecture:
1. **GCP Agent Runtime Model Armor (Layer 1)**: Native cloud-managed filter on inbound and outbound payloads to block jailbreaks, detect toxic language, and redact PII before LLM consumption.
2. **Deterministic Scope Lock Engine (Layer 2)**: Rule-based and intent-based classification that deterministically intercepts diagnostic and prescriptive queries, triggering a standardized non-diagnostic refusal response without invoking downstream generative models.

## Alternatives Considered
- **Prompt-Only Safety System Instructions**: Unreliable against sophisticated adversarial jailbreak attempts and can be bypassed.
- **Post-Processing Only**: Wastes model compute and latency processing unsafe requests that should be rejected immediately.

## Consequences
- **Positive**: Zero exposure to medical diagnosis liabilities, compliance with healthcare AI standards, and zero token costs on rejected queries.
- **Trade-offs**: Strict refusal criteria may reject edge-case clinical queries phrased with personal pronouns; mitigated by clear disclaimer formatting explaining research scope.
