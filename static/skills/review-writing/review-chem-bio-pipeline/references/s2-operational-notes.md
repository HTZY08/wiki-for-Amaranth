# Semantic Scholar API — Operational Notes

## Key Acquisition (Verified 2026-06)

### Reality: Registration Is Effectively Broken

**The API key registration process does not work for most users.** Multiple confirmed reports:

- GitHub SakanaAI/AI-Scientist #104: "I've applied for it nearly five days ago and still haven't received a response"
- The "Request an API Key" link on the API page is a **same-page anchor link** (`#api-key`) that scrolls to a non-functional section — it does NOT trigger any email or form submission
- User conclusion: switch to CORE.ac.uk or use S2 without a key

### What the Broken Flow Looks Like

The actual UX is a modal dialog on the Semantic Scholar main site, NOT a dedicated form:

1. Open https://www.semanticscholar.org/sign-in
2. Click "Create Free Account" → a modal dialog opens ("Join Semantic Scholar")
3. **Critical pitfall:** The checkbox "I accept the Terms of Service & Privacy Policy" MUST be checked before Sign-Up buttons enable. But the checkbox label ALSO contains `<a>` links to ToS/Privacy pages — clicking the wrong spot navigates away from the form instead of toggling the checkbox.
   - **Correct way:** Click the checkbox itself (not the link text). In browser automation, use JS: `document.querySelector('.join-dialog input[type="checkbox"]').checked = true` followed by dispatching a `change` event.
4. After checkbox is toggled, "Sign Up With Google" button enables (was `disabled` before)
   - "Sign Up With Email" button was disabled even after checkbox check — may require a different flow
   - "Sign Up With Your Institution" button remains disabled
5. Click "Sign Up With Google" → triggers Google OAuth redirect

### After Registration (Rarely Works)

- In the unlikely event a key arrives, store in `S2_API_KEY` env var
- Revisit https://www.semanticscholar.org/product/api while logged in — the API key section may appear in the account dashboard
- Key arrives by email IF the registration process functions (unreliable)

### Notes on Browser Automation Attempt

The registration modal was difficult to automate:
- `browser_click` on the checkbox area navigated to ToS page (link in label)
- `browser_console` JS injection (`document.querySelector(...)`) worked to toggle the checkbox
- The Google button click triggered a URL change to `?signIn=true` but didn't complete the flow (likely OAuth popup requirement)
- Conclusion: **have the user do this on their own device.** Google OAuth cannot be automated through the Hermes browser tool.

### What Does NOT Work

- `https://www.semanticscholar.org/register` → 404
- `https://www.semanticscholar.org/product/api#api-key` and `#api-key-form` → both 404 or fail to load
- "Request an API key" link on the API page is an **anchor link** that scrolls to a same-page section, not a separate page

## Rate Limits
- Without key: **Effectively unusable as of 2026.** The shared pool was stated at 100 req/5 min or 1000 req/s globally in older docs, but verified testing shows:
  - First request: 200 OK
  - Second request: 429 (Too Many Requests)
  - This holds whether requests go through a proxy or direct connection (`--noproxy "*"`)
  - Conclusion: the unauthenticated pool is completely exhausted by global bot/tool traffic.
  - **Even 0.33 req/s with exponential backoff fails** — PISMA exhausted 5 retries and got 0 results.
  - Mitigation: do NOT rely on S2 without a key for any automated pipeline. Use OpenAlex/PubMed/CrossRef as primary sources.
- With key: 1 req/s dedicated — stable, but rarely obtainable (see Key Acquisition above)

## PISMA Integration (Verified 2026-06)

**PISMA's S2 client works WITHOUT an API key.** Source code evidence (semantic_scholar_client.py):

```python
headers = {}
if config.api_settings.semantic_scholar_api_key:
    headers["x-api-key"] = config.api_settings.semantic_scholar_api_key
```

The key is entirely optional — if not set, requests go without the `x-api-key` header and S2 serves them at the unauthenticated rate limit.

### Required Config Changes for No-Key PISMA Runs

**⚠️ 2026 UPDATE: Running PISMA with S2 enabled and no API key is essentially a waste of pipeline time.** Even with conservative rate limits, S2 returns 429 on every request after the first. The exponential backoff consumes 1-2 minutes of pipeline wall time per S2 query attempt, producing 0 results. This was verified in a real run:

```
Semantic Scholar: 429 → backoff 5s → 429 → backoff 10s → 429 → backoff 20s → 429 → backoff 30s → 429 → GIVE UP
Total time wasted on S2: ~65 seconds per query → ~2+ minutes total
Results from S2: 0
```

**Recommendation: Disable `semantic_scholar_enabled` in the PISMA config unless you have an API key.** The other sources (OpenAlex, PubMed, Crossref, Unpaywall) will produce 100+ papers on their own, which is sufficient for a review.

```json
{
  "semantic_scholar_enabled": false
}
```

If you MUST keep S2 enabled (e.g., for its citation graph), use these aggressive limits to minimize damage:

```bash
python main.py run --config gold_review_config.json \
  --semantic-scholar-calls-per-second 0.1 \
  --semantic-scholar-max-requests-per-minute 5 \
  --semantic-scholar-request-delay-seconds 10.0 \
  --semantic-scholar-retry-attempts 1
```

**PISMA alternative sources that work without keys:** OpenAlex, PubMed, Crossref, Unpaywall — all verified working in 2026.

## Fallback Chain (verified 2026-06)
```
S2 429/offline
  → Retry is pointless — even 0.1 req/s will 429 on the 2nd request.
  → Skip S2 entirely. Disable in PISMA config: semantic_scholar_enabled: false
  → OpenAlex for known-item DOI lookup (cited_by_count, concepts, related_works)
  → CrossRef for cited-by counts and DOI verification (free, reliable)
  → AI search only for recent preprints; mark [UNVERIFIED]
```

## Proxy Setup
- WSL mihomo proxy at 127.0.0.1:7890
- Start: /opt/data/bin/mihomo -d /opt/data/mihomo-config
- Keepalive: /opt/data/scripts/mihomo-keepalive.sh
- S2 goes through proxy automatically via env vars
