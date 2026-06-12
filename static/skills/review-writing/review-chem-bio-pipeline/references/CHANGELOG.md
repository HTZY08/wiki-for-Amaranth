### v0.9 — Add "Don't Assume" Rule, S2 Key Strategy

- Added ⚠️ Critical Rule in Phase 1: never default user's topic to their known research background — ask first.
- S2 key acquisition guide documented (request at semanticscholar.org, stored in `S2_API_KEY` env var, 1 req/s with key).
- S2 fallback chain confirmed: when 429, use OpenAlex for known-item lookup + CrossRef for cited-by counts.
