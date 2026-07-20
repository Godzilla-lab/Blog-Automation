# Hexa , Free Operations Audit Funnel: Backend Build & Optimization Spec

**Purpose of this document:** a self-contained brief another AI/developer can build and iterate on, with no prior conversation context. Goal = convert ad clicks into **booked, qualified, showed-up audit calls** and then into **paid implementation clients**, on a "pay-after-we-save-you" model.

**The one job of this backend:** everything after the click. Maximize (clicks → qualified bookings → show-ups → closes), and instrument it so it can be optimized weekly.

---

## 0. RECOMMENDED DEFAULTS (build against these; OWNER should confirm/change the ⚠️ ones)
**Market = NIGERIA (decided 2026-06-29).** Defaults filled so the build isn't blocked. ⚠️ items still need the owner's real call.
- **Market / geography:** **NIGERIA, billed in ₦ (naira).** Decided. **CTA channel = BOTH Click-to-WhatsApp AND a form/booking** (owner chose both, 2026-06-29) , WhatsApp is still the highest-converting contact method in NG (opens Meta's 72-hr free window), the form is the more premium door; offer both, let the lead pick. **The OFFER is broad operations automation, NOT WhatsApp-reply automation** (that angle is saturated in NG) , keep WhatsApp purely as a contact door, never the pitch. **No niche** , general Nigerian mid-to-large companies (owner declined to narrow). **Do NOT lead with the word "AI" in cold copy** , it is scam-coded locally (CBEX / AI-Ponzi fallout); lead with the concrete money/time outcome and call it "systems / automation." Trust cues are make-or-break: real Nigerian faces, named + located testimonials ("Tunde, Lagos"), Paystack/Flutterwave marks, ₦ pricing shown, fast WhatsApp replies. Native/authentic beats glossy (glossy triggers scam-radar).
- **Target vertical (v1):** **Growing Nigerian companies, mid-to-large** (operations-heavy: distribution/logistics, manufacturing, clinics/hospitals, schools, real estate, professional-services firms). Start with 1-2 sectors , a sharp niche converts better than "all businesses." ⚠️ *Owner: confirm which 1-2 sectors (and confirm the "jewelry" mention , niche or transcription slip).*
- **Price model:** **Build fee + performance share**, in ₦. Default: a setup/build fee `[₦X]` + `[25-50%]` of verified savings, OR a flat ₦ retainer that unlocks once a savings threshold is hit. ⚠️ *Owner: set the real ₦ fee + %.*
- **Savings measurement (default):** hours × loaded labour cost baseline, in ₦, signed off before and after (30/60/90-day window). Delta = verified savings; bill the agreed %. ⚠️ *Owner: confirm enforceable.*
- **Real proof:** real or clearly-illustrative only. Use `[REAL_CLIENT_RESULT]` placeholders until verified. Never invent client numbers.

---

## 1. OFFER SUMMARY (context for the builder)
- **Offer:** A free "Operations Leak Audit." We analyze a company's workflows, deliver a **"Leak Report"** showing exactly where they lose time and money, then implement automation to fix it. **They pay only after we deliver measurable savings** ("no savings, no fee").
- **Why it works (validated):** This is the 30-year-proven cost-reduction-audit model (P3 Cost Analysts "no savings = no fee"; PRGX "don't pay until you receive recoveries," trusted by 1/3 of the Fortune 500). We are cloning a proven structure, not inventing one.
- **Named mechanism (use everywhere):** "The Leak Report" / "Operations Leak Audit." Never call it a "free consultation" or "discovery call."

---

## 2. RESEARCH-BACKED PRINCIPLES (the rules this funnel must obey)
The builder should treat these as constraints, each is evidence-based:
1. **Message-to-awareness match.** Cold traffic is problem-aware, not ready to "buy." Lead with the *leak/problem*, not "book a call with us." (Eugene Schwartz awareness levels.)
2. **Ad ↔ landing page congruence.** The LP headline must mirror the ad that brought them. Mismatch tanks conversion. (Build 1 LP variant per ad angle, see §4.)
3. **Show the deliverable.** The "Leak Report" artifact is the hero, on the ad, the LP, and the call. (SEOptimer's graded-report ad ran 146 days; Foleon's "send us your asset" ran 809 days.)
4. **Named mechanism / Container noun.** Brand the "how." (Hormozi M.A.G.I.C.; Schwartz mechanism.)
5. **Risk-reversal is the hook.** "No savings, no fee. No kickbacks." (P3, SIB, Schooley Mitchell.)
6. **Qualify before the call.** Free audits attract tire-kickers; a qualification gate is mandatory for a high-ticket offer. (AutoFlow Labs warning; high-ticket lead-gen literature.)
7. **Instant follow-up.** Auto SMS/email the second a lead comes in; minutes matter. (Slow response = lead books a competitor.)
8. **Low-friction capture.** Short form (1-4 fields converts ~4x better than 8+; native lead forms cut CPL ~80% , Ladder.io). Add qualification *after* the cheap capture, or as a quiz.
9. **Value-named CTA, first person.** "Get My Free Leak Report," "Book My Operations Leak Review", never "Submit"/"Learn More."
10. **Optimize for the post-qualification event, not raw leads.** (Firing the conversion event only after qualification improved lead→SQL ~19% in one documented case.)

---

## 3. THE FULL CONVERSION PATH (the flow to build)
```
AD CLICK
  → LANDING PAGE (congruent, leak-led, shows the Leak Report)        [§4]
     → LEAD CAPTURE (short form OR Click-to-WhatsApp)                [§5]
        → QUALIFICATION (3-4 questions / quiz)                       [§6]
           → if QUALIFIED  → BOOKING (value-named slot)             [§7]
           → if NOT qual.  → nurture sequence / self-serve resource [§6]
        → INSTANT FOLLOW-UP (SMS+email within 60s) fires on capture  [§8]
  → PRE-CALL NURTURE (reminders + value, no-show reduction)          [§8]
  → AUDIT CALL: run audit live OR present prepared Leak Report       [§9]
     → REVEAL (the leaks + $ quantified) → PROPOSE (pay-after-save)  [§10]
  → CLOSE → ONBOARDING → FULFILLMENT (build the automations)         [§11]
  → SAVINGS MEASUREMENT → BILLING (pay-after-savings)                [§9]
EVERYTHING instrumented for weekly optimization                      [§12]
```

---

## 4. LANDING PAGE SPEC (the core post-click asset)
Build **one LP per ad angle** for congruence (5 ad angles exist: Leak Report, Pain-question, No-savings-no-fee, Bold-stat, Native-founder). Same template, swapped hero headline to match the ad.

**Global LP requirements**
- Mobile-first, sub-2s load, one primary CTA repeated 3-4x down the page.
- Currency + trust cues per market (₦ + WhatsApp for Nigeria; $ + calendar for US/global).
- No top nav that lets people escape (dedicated funnel LP, not the main site).

**Section-by-section (top to bottom):**
1. **Hero (above the fold)**
   - Eyebrow: audience callout , `FOR [TARGET]` (e.g. "FOR GROWING COMPANIES").
   - Headline: the leak + a number, mirrors the ad. e.g. *"Most companies leak 8-12 hours a week to manual work , and can't see where."*
   - Sub: the offer + named deliverable + risk-reversal. *"Get a free Operations Leak Audit. We show you exactly where the time and money go , a Leak Report in [X days]. You only pay after we deliver savings."*
   - Primary CTA button: `Get My Free Leak Report`.
   - Visual: the Leak Report artifact (graded report mockup).
   - Micro-trust under CTA: *"No obligation. No upsells. Keep your current tools. ~[N] hours of your time."*
2. **Problem / agitation** , 3 bullet "leaks" the target feels (manual data entry, slow follow-up, double-handling). Put the status quo on a $ or hours clock.
3. **What you get (the deliverable)** , show the Leak Report contents: a score, the specific leaks found, the $ at risk, the fix roadmap. Make it tangible ("a [N]-page report / a score out of 100").
4. **How it works** , 3 simple steps: (1) Book the audit, (2) We map your operations (~N hrs of your time), (3) You get the Leak Report + we fix it, pay only after savings.
5. **Proof** , real testimonials with NAME + COMPANY/LOCATION, or `[REAL_CLIENT_RESULT]` placeholders. One concrete $/% number if real. Logos if any. (Expert/named proof > anonymous.)
6. **Risk-reversal block** , the model as the guarantee: *"No savings, no fee. We don't get paid until you do. No kickbacks , our pay only comes from the savings we prove."*
7. **FAQ / objection handling** , "What's the catch?", "How much of my time?", "What if you find nothing?", "Is my data safe?", "How do you measure savings?"
8. **Final CTA** , repeat the booking CTA + the micro-trust line.

**Copy is owned by this funnel; never send cold traffic to the generic company homepage.**

---

## 5. LEAD CAPTURE
- **Two valid patterns , pick per market:**
  - **US/global:** embedded short form (Name, Work email, Company, Company size) → then qualification → calendar. OR Meta native lead form (cheapest CPL).
  - **Nigeria:** **Click-to-WhatsApp** as primary (Nigerians convert in chat, not forms; opens Meta's 72-hr free-messaging window). Qualify in the chat.
- Keep initial capture to **≤4 fields**. Heavier qualification comes next, not here.
- Fire the **instant follow-up** (§8) and the **capture event** (§12) on submit.

---

## 6. QUALIFICATION (the tire-kicker filter)
A short quiz/form (3-4 Qs) right after capture, or built into the WhatsApp flow:
- Company size / revenue band (the main fit filter).
- "What's costing your team the most time right now?" (multiple choice , reveals the pain + intent).
- "When are you looking to fix this?" (timeline = intent).
- Optional: current tools / team size.
**Logic:**
- **Qualified** (fits size + has a real pain + near-term timeline) → straight to booking (§7).
- **Not qualified** → polite redirect: a self-serve resource / "we'll send you a DIY leak checklist" + nurture sequence (don't burn them, nurture them).
**Only qualified leads should trigger the "booked qualified call" conversion event** that ad optimization is trained on (§12).

---

## 7. BOOKING
- Calendar tool (Calendly / Cal.com / GoHighLevel) embedded post-qualification.
- **Value-named call:** "Operations Leak Review" or "Leak Report Walkthrough", NOT "discovery call."
- Collect the few extra context fields on booking.
- Set expectation: "On this call we walk through where your operations are leaking time and money."
- Trigger booking confirmation + calendar invite + reminder sequence (§8).

---

## 8. AUTOMATED FOLLOW-UP & NURTURE (instant + ongoing)
This is where most funnels leak , build it carefully.
- **On capture (within 60s):** SMS + email confirming + next step. ("Thanks [name], here's your booking link / an attorney/specialist will reach out.")
- **On booking:** confirmation + calendar invite + "what to expect" + ask them to bring [1 simple input].
- **Pre-call reminders:** 24h + 1h before (SMS+email) , cuts no-shows.
- **No-show recovery:** immediate "missed you" + easy rebook, 3-touch.
- **Unqualified nurture:** value sequence (the DIY leak checklist, a case study, a soft re-qualify) so they convert later.
- **Post-call:** the Leak Report delivery + proposal + follow-up cadence until decision.
Tooling: GoHighLevel (all-in-one) OR Make/n8n + Twilio + email (SendGrid/Resend). Nigeria: WhatsApp Business API / Twilio WhatsApp.

---

## 9. THE AUDIT + LEAK REPORT (the deliverable) & PAY-AFTER-SAVINGS MECHANICS
**The Leak Report (productize this , it's the artifact in the ad/LP and the thing you hand over):**
- Standardized template: an **Operations Efficiency Score** (e.g. out of 100 or a grade), a list of **specific leaks** (process, hours/week lost, $/month at risk), and a **fix roadmap** (what to automate, expected saving).
- A repeatable **audit process / checklist** so any operator can run it consistently (intake of their workflows → map manual/repetitive tasks → quantify time+cost → rank by ROI).
- Keep it a **2-4 page diagnostic**, not a full free implementation plan (giving away the whole roadmap kills the paid close).

**Pay-after-savings model (the trickiest piece , define explicitly):**
- **Baseline:** measure the current cost of the target process (hours × loaded labor cost, or the hard $ leak) BEFORE building. Document it, both parties sign off on the baseline.
- **Savings definition:** agree in writing what counts (hours saved × rate, reduced spend, recovered revenue). Tie it to the baselined process only.
- **Measurement window:** e.g. 30/60/90 days post-implementation.
- **Billing trigger:** invoice a % of verified savings (or a flat fee unlocked once a savings threshold is hit). Define the % / fee. Include a floor or cap if needed.
- **Contract:** a simple agreement covering baseline, savings definition, measurement method, billing, and a "no savings, no fee" clause. (Mirror P3/PRGX contingency contracts.)
- **Risk control for you:** scope to ONE high-confidence automation first (don't promise savings on everything). Land → prove → expand.

---

## 10. THE CALL → CLOSE (script skeleton for the operator)
1. Reconfirm their pain (from the qualification answers).
2. **Reveal the Leak Report** , walk the score + the specific leaks + the $ at risk. Let the number land.
3. Tie each leak to a fix and an expected saving.
4. **Propose:** "We'll implement [the top fix]. You pay [%/fee] only after we deliver [baselined] savings. No savings, no fee."
5. Handle objections (catch / time / data / measurement , pre-answered in FAQ).
6. Close to onboarding (sign the agreement, book kickoff).

---

## 11. FULFILLMENT (post-close, brief , separate build track)
- Onboarding checklist + access/inputs needed.
- Build the automations (the actual delivery , scope per client).
- Milestone updates; measure savings (§9); trigger billing.
- Upsell/expand once the first win is proven.
*(Detailed fulfillment SOPs are a separate doc; this funnel spec ends at the close + measurement handoff.)*

---

## 12. TRACKING & OPTIMIZATION (so it can be improved weekly)
**Events to track (in this order , optimize ads on the LATE ones):**
- `LP_view` → `lead_capture` → `qualified` → `call_booked` → `call_showed` → `closed_won` → `savings_delivered`.
- **Train Meta/ad optimization on `qualified` or `call_booked`, NOT raw `lead_capture`** (avoids junk-lead optimization; ~19% SQL lift documented).
- Pass these back to the ad platform via Conversions API / offline conversions.

**Core metrics + rough benchmarks to beat (directional, from research):**
- LP conversion (visit → capture): aim 4-10%+ (audit offers sit between gated content and demo-request).
- Capture → qualified: depends on filter; track it.
- Qualified → booked: target 60%+ (median for qualified B2B leads ~62%).
- Booked → showed: 60-80% with the reminder sequence.
- Cost per qualified call: track and drive down (the real north-star CPA).

**Optimization loop (weekly):**
1. Read the funnel report; find the biggest drop-off stage.
2. Form ONE hypothesis for that stage; change ONE thing (headline, form length, qualification logic, reminder timing).
3. A/B test it; keep the winner; re-measure.
4. On the ad side, run a hook × format matrix; kill the bottom ~half each week; scale winners.
5. Keep ad ↔ LP congruence intact when you swap creative.

**Instrumentation stack:** GA4 + the ad platform's pixel/CAPI + the CRM's reporting; a single funnel dashboard (e.g. in the CRM or a sheet) showing the event counts + rates above.

---

## 13. RECOMMENDED TECH STACK (pick one lane)
- **All-in-one (fastest):** GoHighLevel (LP + forms + calendar + SMS/email + WhatsApp + CRM + pipelines + reporting). Best for a solo operator who wants it working fast.
- **Composable:** Webflow/Framer/Unbounce (LP) + Typeform/Tally (quiz) + Cal.com/Calendly (booking) + Make or n8n (automation) + Twilio (SMS/WhatsApp) + Resend/SendGrid (email) + a CRM (HubSpot free / Pipedrive) + GA4 + Meta CAPI.
- **Nigeria note:** prioritize WhatsApp Business API; ensure naira billing on the ad account.

---

## 14. BUILD ORDER (for the other Claude , do in this sequence)
1. **Leak Report template + audit process** (§9) , the deliverable must exist first.
2. **Pay-after-savings agreement + measurement method** (§9) , makes the offer real/enforceable.
3. **Landing page** (§4) for the top ad angle, then variants.
4. **Capture + qualification + booking** (§5-7).
5. **Follow-up automations** (§8).
6. **Tracking + dashboard** (§12).
7. **Optimization loop** , ongoing.

**Each stage: build → test with a real/sample lead → confirm the event fires → move on. Report drop-offs back for iteration.**
