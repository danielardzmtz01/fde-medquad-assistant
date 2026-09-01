# ADR 0001: Multi-Agent Hierarchy via Google Agent Development Kit (ADK)

## Status
Accepted

## Context
Clinical question answering requires multiple distinct cognitive steps: parsing intent, executing vector search over NIH medical literature, synthesizing referenced facts, verifying citation fidelity, and screening for medical advice liabilities. 

A single monolithic LLM prompt struggles to maintain strict medical guardrails while executing tool calls and generating citations, leading to higher hallucination rates and complex prompt maintenance.

## Decision
We adopt a hierarchical multi-agent architecture powered by the Google Agent Development Kit (ADK):
1. **RootOrchestrator**: Acts as the conversational supervisor, routes queries to specialized subagents, handles error degradation, and formats user-facing payloads.
2. **ResearcherAgent**: Focuses exclusively on calling the Vertex AI Search tool and synthesizing medical summaries using Gemini 2.5 Pro.
3. **ReviewerAgent**: Serves as an independent clinical fact-checker using Gemini 2.5 Flash, evaluating whether all factual statements in the draft are strictly grounded in the retrieved NIH chunks.

## Alternatives Considered
- **Monolithic Single-Agent ReAct Loop**: Easier to implement initially, but suffered from prompt bloat, mixed responsibilities, and higher rate of missed citations.
- **Sequential LangChain Pipeline**: Rigid DAG structure that lacks dynamic multi-agent self-correction and recovery loops.

## Consequences
- **Positive**: High modularity, independent unit-testability of each agent, strict separation of concerns, and verifiable fact-checking gate before delivery.
- **Trade-offs**: Slightly increased end-to-end latency (~1.5s vs 1.0s) due to the reviewer validation step; mitigated by running Gemini 2.5 Flash for the reviewer.
