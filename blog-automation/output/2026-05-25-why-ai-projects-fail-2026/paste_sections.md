# Paste sections for hexaaiagency.com admin (per-field)

> Copy each section into the matching field in the rich-text admin. The BODY (HTML) section is the same content saved separately as `article.html` for one-shot paste into the rich-text editor. The Markdown rendering for reviewers is in `blog_post.md`.

---

### TITLE

Why AI Projects Fail in 2026: The Honest ROI Truth

---

### SLUG

why-ai-projects-fail-2026

---

### EXCERPT

Most AI projects in 2026 stall before they show ROI. Here's the real reason, the 2026 data nobody puts on a deck, and the 7-question buyer diagnostic.

---

### BODY (HTML)

> See `article.html` in this folder. Paste the entire file contents into the rich-text editor as HTML.

---

### COVER IMAGE BRIEF

A flat-style illustration of a clipboard with a single number circled in red, sitting on a desk between a chatbot avatar and a dollar-sign icon. Use the brand accent color. No stock photos of "AI futures" or abstract neural networks.

Alt text: "Diagnostic-first framework for measuring AI project ROI in 2026, illustrated with a circled baseline metric between a chatbot and a dollar sign."

---

### INLINE IMAGE BRIEFS

None for this post. The data block in H2 #3 (AI project failure rate) is rendered as a styled list and does not need a chart image. If the operator wants to add one later, a horizontal bar chart of the 6 stats from H2 #3 (Gartner 60%, MIT NANDA 95%, McKinsey value concentration, BCG GenAI bottom-line gap, RAND 2x fail rate, Forrester chatbot business case) would slot in cleanly above the list.

---

### INTERNAL LINKS USED

- /about/team — "Hexa AI Agency" (first mention in the diagnosis-first framework section)
- /case-studies/ai-chat-system — "Build A is an on-site chatbot we shipped" (prefixed with "Illustrative composite from recent engagements")
- /services/ai-agent-development — "Our AI agent development engagements"
- /services/ai-workflow-automation — "we run this on AI workflow automation engagements"
- /services/customer-service-automation — "customer service automation" (in the closing CTA)

---

### EXTERNAL CITATIONS USED

> Every URL below was returned by a Tavily search at write time and HEAD-checked. Spot-verify each landing page resolves before clicking publish in the admin.

- https://www.gartner.com/en/newsroom/press-releases/2026-04-07-gartner-says-artificial-intelligence-projects-in-infrastructure-and-operations-stall-ahead-of-meaningful-roi-returns — Gartner April 2026 press release on AI in I&O projects stalling. Cited in the lead and in the failure-rate data block.
- https://complexdiscovery.com/why-95-of-corporate-ai-projects-fail-lessons-from-mits-2025-study — Analysis of the MIT NANDA 2025 study finding 95% of generative AI pilots produce zero measurable revenue. Used as a secondary source because the original NANDA project page is hard to permalink. Spot-verify the analysis matches the primary source.
- https://www.mckinsey.com/~/media/mckinsey/business%20functions/quantumblack/our%20insights/the%20state%20of%20ai/2025/the-state-of-ai-how-organizations-are-rewiring-to-capture-value_final.pdf — McKinsey 2025 State of AI report PDF (hosted on mckinsey.com). Cited for the value-capture concentration claim.
- https://www.bcg.com/publications/2024/from-potential-to-profit-with-genai — BCG 2024 report on GenAI bottom-line impact and operating-model change. Cited in the failure-rate data block.
- https://www.rand.org/pubs/presentations/PTA2680-1.html — RAND presentation on AI deployment risk and root-cause misalignment. Cited twice (in "the real reason" and in the data block).
- https://www.forrester.com/blogs/build-the-right-chatbot-business-case — Forrester blog post on building the chatbot business case. Cited in the data block. This is the v4 swap (replacing the earlier "People avoid chatbots" URL, which supported the adoption gap rather than the renewal-attribution argument). The diagnosis-first framework section references this same source by name without a second hyperlink (to stay within the 12 external-link cap).
- https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering — Anthropic prompt engineering docs (deep-link, not the homepage). Cited in the 30-day pilot section.
- https://cal.com/hexaiagency — Booking link in the closing CTA. (Not a citation; included for completeness.)

---

### V4 CHANGE LOG

Changes from v3 in response to the 2026-06-02 second reviewer pass (which scored v3 at 87/100):

1. **Forrester citation swap.** The data-block bullet now links `forrester.com/blogs/build-the-right-chatbot-business-case` (matches the renewal-attribution argument the sentence actually makes) instead of the "People avoid chatbots" URL (which supports the adoption gap, not the attribution argument). Wording tightened to match.
2. **Anthropic docs deep-link.** Swapped `docs.anthropic.com/` for `docs.anthropic.com/en/docs/build-with-claude/prompt-engineering` to satisfy the "load-bearing external links" criterion.
3. **Pilot price band restored.** "$8,000 to $25,000" returned in both body and FAQ. v3 had over-softened this to "four-to-five-figure range", which lost credibility per the reviewer.
4. **H2 #1 expansion.** Added a one-paragraph buyer-side tell ("the contract names a feature, not a metric") to bring the section over the 200-word target.
5. **H2 #4 expansion.** Added a one-paragraph vendor pattern ("the proposal lists capabilities without naming a P&L line") for the same reason.
6. **Build A/B sharpened.** The chatbot composite now describes the attribution mechanic (session ID handed off to CRM) without inventing a specific metric.
7. **Skipped the reviewer's #1 EEAT recommendation.** The reviewer suggested replacing the "Illustrative composite" Build A/B with one real anonymized engagement with specifics ("22-location home-services client, answer rate 62% → 89% over 8 weeks"). That would re-introduce the exact fabrication class the prior reviewer caught. To safely earn this EEAT lever, operator needs to supply a real engagement (industry + scale + actual metric movement) that can be defended if challenged.

### V3 CHANGE LOG (kept for history)

1. Removed the Robert Potter Threads attribution entirely.
2. Removed every unsourced quantified HEXA-internal claim ("more than 30 businesses", "$58K-$120K", "92% renewal", "prior cohort under 20%", Build A/B specific numbers).
3. Prefixed Build A/B with `<em>Illustrative composite from recent engagements.</em>`
4. Added internal link to `/about/team` for first "Hexa AI Agency" mention.
5. Added internal link to `/services/customer-service-automation` in closing CTA.
6. Added Source link to RAND in the data-block bullet.
7. Anchored the diagnosis-first framework's renewal claim to Forrester (later upgraded in v4).
8. Softened the pilot budget claim (later reverted in v4).
