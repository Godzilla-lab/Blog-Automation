"""
Generate a large batch of human-sounding tweets (100-300+)
Creates a library you can pull from for weeks
"""

import json
from datetime import datetime
from pathlib import Path

def generate_tweet_library():
    """Generate 300 human-sounding tweets across different categories"""

    tweets = []

    # Category 1: Hot Takes (60 tweets)
    hot_takes = [
        "been in AI for 3 years — biggest myth? that you need a tech background. best automations I've seen came from people who just understood their business deeply",
        "unpopular opinion: most AI agencies are solving the wrong problems. clients don't need more features, they need 3 things done really well",
        "spent $40k testing AI tools last year — learned that the free tier of Claude beats most $500/mo enterprise solutions if you know what you're doing",
        "real talk: if your AI demo takes more than 2 minutes to show value, you've already lost the client",
        "everyone's building AI chatbots. nobody's asking if customers actually want to talk to a bot instead of just finding the answer themselves",
        "the AI agencies winning right now? they're not the ones with the best tech. they're the ones who can explain ROI in plain English",
        "hot take: AI won't replace jobs, it'll expose the people who were coasting on repetitive tasks and reward the ones who think critically",
        "most 'AI solutions' are just expensive wrappers around ChatGPT that someone's charging $5k/month for. learn the API, save your money",
        "biggest lesson from automating 100+ workflows: the bottleneck is never the AI. it's getting people to actually describe what they want",
        "controversial: if you can't build it with a good prompt and basic API calls, you probably don't understand the problem yet",
        "AI tools are like gym memberships — everyone buys them, nobody uses them to their full potential",
        "been testing Opus 4.5 for a week. it's not just better, it's different. like switching from a calculator to a coworker",
        "the AI hype cycle is wild — 6 months ago everyone wanted agents, now they just want their email to write itself",
        "clients always ask for custom models. what they actually need is 3 well-crafted prompts and a Zapier connection",
        "unpopular take: AI agents are overkill for 90% of businesses. most need better processes before better technology",
        "spent 2 years building complex AI systems. best ROI? a 50-line Python script that saves clients 10 hours/week",
        "everyone's obsessed with AI replacing humans. real opportunity is AI helping humans stop doing soul-crushing repetitive work",
        "the AI companies that'll win: the ones building tools so simple your grandma could use them, not the ones flexing technical complexity",
        "hottest take I have: most AI startups are building solutions looking for problems instead of solving actual pain points",
        "AI coding assistants are great but nobody talks about how they're teaching bad developers to write more bad code faster",
        "controversial opinion: if your AI solution requires training your team for more than 1 hour, you built it wrong",
        "been automating businesses for 2 years — the pattern? companies waste more time deciding what to automate than actually automating it",
        "AI pricing is broken. paying per token is like paying per keystroke. we'll look back at this and laugh",
        "everyone wants to build the next ChatGPT. meanwhile there's billions in just helping people use the one that exists",
        "unpopular: AI agents that 'think' for 30 seconds aren't impressive, they're inefficient. optimize your prompts better",
        "watching AI Twitter is exhausting. half the 'breakthroughs' are just better prompt engineering with a new name",
        "the AI tools getting the most hype aren't the ones solving real problems, they're the ones with the best marketing",
        "controversial: most businesses don't need AI, they need a competent operations person who knows how to use spreadsheets",
        "spent $100k on AI R&D last year. best investment? $20/mo Claude subscription and learning to write good prompts",
        "everyone's racing to AGI. meanwhile businesses are drowning in tasks that dumb automation could solve today",
        "hot take: AI consultants charging $10k for 'strategy' are mostly just writing prompts and calling it innovation",
        "the future isn't fully autonomous AI agents. it's AI that makes humans 10x more effective at what they already do",
        "biggest scam in AI: companies selling 'proprietary models' that are just fine-tuned GPT wrappers with a 5000% markup",
        "unpopular opinion: if you're not shipping AI solutions in days (not months), you're overthinking it",
        "been building AI products for 3 years — users don't care about your tech stack. they care if it saves them time",
        "controversial take: the AI bubble isn't in the technology, it's in the consulting fees people are charging for basic implementations",
        "most AI agencies: 'we build custom solutions' // what they actually do: connect APIs and charge $50k",
        "AI democratization is real but nobody talks about how it's making mediocre developers think they're great developers",
        "unpopular: spending 6 months building an AI agent when you could just hire a VA for $15/hr is not innovation, it's ego",
        "the best AI implementation I've seen was 20 lines of code that saved a company $200k/year. complexity isn't the goal",
        "hot take: if your AI pitch includes the words 'paradigm shift' you've already lost technical credibility",
        "everyone's building AI products. almost nobody is building AI products that people actually want to pay for",
        "controversial: most AI automation fails not because of technology, but because people don't actually want to change their workflow",
        "AI Twitter is 90% people announcing projects and 10% people shipping. be the 10%",
        "spent 2 years in AI — biggest surprise? clients trust AI recommendations more than human ones, even when the AI is wrong",
        "unpopular opinion: if you need a AI engineer on staff to maintain your AI solution, you sold them the wrong solution",
        "the AI race isn't about who builds AGI first, it's about who makes AI actually useful for normal people first",
        "hot take: prompt engineering isn't a real job, it's a temporary skill gap that will be automated away in 2 years",
        "watching startups pivot to 'AI-powered' is like watching everyone add 'blockchain' in 2017. most of it's unnecessary",
        "controversial: the best AI products are the ones where you don't even know you're using AI",
        "been automating workflows for years — pattern: people want AI to do creative work but won't let it touch their email. should be opposite",
        "AI demos that work perfectly are lies. AI in production that works 95% of the time is reality. plan accordingly",
        "unpopular take: most people using AI to write tweets should just learn to write better tweets",
        "the AI companies surviving 5 years from now won't be the ones with the best models, they'll be the ones with the best distribution",
        "controversial opinion: if your AI saves me 10 minutes but takes 30 minutes to learn, it's a bad product",
        "everyone's building AI agents to replace workers. real opportunity is building AI that makes workers not hate their jobs",
        "hot take: AI marketing tools that promise to '10x your content' usually just 10x your bad content",
        "spent $50k on AI experiments — ROI came from the simplest implementations, not the complex ones I was proud of",
        "unpopular: if you're charging clients for 'AI consulting' but just telling them to use ChatGPT Plus, you're scamming them",
        "the future is boring. it's AI quietly handling annoying tasks in the background, not flashy demos that wow investors"
    ]

    # Category 2: Before/After Results (50 tweets)
    before_after = [
        "automated client onboarding last month\n\nbefore: 6 hours per client\nafter: 12 minutes\n\nused: Claude + Airtable + Zapier\ncost: $67/month\n\nROI in week 1",
        "we rebuilt a client's customer support workflow\n\nbefore: 4 agents, 200 tickets/day, 8hr response time\nafter: 2 agents + AI triage, same volume, 45min response\n\nsaved $120k/year",
        "implemented AI lead scoring for B2B client\n\nbefore: sales team wasted 60% of time on cold leads\nafter: AI pre-qualifies, team focuses on hot leads only\n\nclose rate went from 8% to 23%",
        "automated content repurposing for agency\n\nbefore: 1 blog post = 1 piece of content\nafter: 1 blog post = 8 optimized pieces across platforms\n\nsame effort, 8x output",
        "built AI email sorter for exec\n\nbefore: 3 hours/day in inbox\nafter: 20 minutes on what matters\n\nfreed up 14 hours/week for actual strategy",
        "deployed meeting summarizer for remote team\n\nbefore: 2 hours of meetings + 1 hour writing notes = 3 hours\nafter: AI handles summaries automatically\n\nteam got 5 hours/week back",
        "created AI social media scheduler\n\nbefore: 10 hours/week creating and posting content\nafter: 2 hours curating, AI handles rest\n\n$0 cost using free APIs",
        "implemented invoice processing automation\n\nbefore: 2 people, 3 days to process monthly invoices\nafter: AI extracts data, 4 hours to review\n\nsaved 2 full salaries",
        "built proposal generator for consulting firm\n\nbefore: 6 hours per proposal, 40% win rate\nafter: 45 minutes per proposal, 55% win rate\n\nmore wins, less time",
        "automated customer feedback analysis\n\nbefore: manually reading 500+ reviews/month\nafter: AI surfaces patterns and urgent issues\n\ncut response time from 2 weeks to 2 days",
        "deployed chatbot for SaaS company\n\nbefore: support team answering same 20 questions daily\nafter: bot handles 70% of tier-1 questions\n\nteam now focuses on complex issues",
        "created content calendar automation\n\nbefore: 8 hours/month planning social posts\nafter: AI generates calendar based on trends\n\n10 minutes to review and approve",
        "built document search for law firm\n\nbefore: associates spending 5 hours/week finding precedents\nafter: AI finds relevant cases in seconds\n\nbillable hours increased 12%",
        "implemented sales email personalization\n\nbefore: generic cold emails, 2% response rate\nafter: AI personalizes based on LinkedIn/website\n\n14% response rate",
        "automated expense report processing\n\nbefore: finance team, 2 days/month on expenses\nafter: AI categorizes and flags issues\n\n4 hours total time",
        "deployed resume screening for HR\n\nbefore: 200 resumes = 10 hours of initial review\nafter: AI shortlists top 15 candidates\n\n45 minutes to review finalists",
        "built competitor monitoring system\n\nbefore: manually checking 20 competitor sites weekly\nafter: AI tracks changes and alerts on updates\n\nzero manual work",
        "created onboarding workflow automation\n\nbefore: new hires overwhelmed, 30% failed in first month\nafter: AI delivers personalized training path\n\nretention improved to 95%",
        "implemented inventory forecasting\n\nbefore: constantly out of stock or overstock\nafter: AI predicts demand based on trends\n\nreduced waste by 40%",
        "automated blog post SEO optimization\n\nbefore: writer creates post, SEO person optimizes (8 hours total)\nafter: AI suggests optimization during writing\n\n3 hours total, better results",
        "built meeting scheduler for sales team\n\nbefore: 47 emails average to schedule 1 meeting\nafter: AI finds optimal time, books automatically\n\n3 emails average",
        "deployed customer churn prediction\n\nbefore: reactive — lose customers, wonder why\nafter: AI flags at-risk accounts 2 weeks early\n\nreduced churn 35%",
        "automated quality assurance checks\n\nbefore: QA team manually testing every feature\nafter: AI handles regression testing\n\nQA focuses on complex scenarios only",
        "created social listening dashboard\n\nbefore: marketing intern manually tracking brand mentions\nafter: AI monitors 24/7, surfaces urgent items\n\nsaved 20 hours/week",
        "implemented dynamic pricing for ecommerce\n\nbefore: manually adjusting prices monthly\nafter: AI optimizes based on demand/competition\n\nrevenue up 18%",
        "built knowledge base from support tickets\n\nbefore: same questions answered 1000+ times\nafter: AI creates FAQ from ticket patterns\n\nticket volume down 40%",
        "automated contract review process\n\nbefore: legal team reviewing every vendor contract (6 hours each)\nafter: AI flags concerning clauses\n\n45 minutes per contract",
        "deployed recruitment outreach automation\n\nbefore: recruiter manually messaging 50 candidates/day\nafter: AI personalizes and sends 200/day\n\n4x reach, same quality",
        "created financial forecasting model\n\nbefore: CFO spending week on quarterly forecast\nafter: AI model updates in real-time\n\n1 hour to review and adjust",
        "built customer journey mapper\n\nbefore: guessing at what path customers take\nafter: AI tracks and visualizes actual behavior\n\nconversion rate up 28%",
        "automated partnership outreach\n\nbefore: BD team cold emailing 30 prospects/week\nafter: AI identifies best fits, drafts personalized intro\n\n100 prospects/week, higher response",
        "implemented smart task prioritization\n\nbefore: team constantly asking 'what should I work on?'\nafter: AI assigns priorities based on impact\n\nproductivity up 45%",
        "created video content repurposing\n\nbefore: 1 webinar = 1 piece of content\nafter: AI generates clips, posts, blogs from same video\n\n1 webinar = 15 pieces",
        "built anomaly detection for SaaS metrics\n\nbefore: finding issues in dashboards after customers complained\nafter: AI alerts on unusual patterns immediately\n\ncatch problems before they escalate",
        "automated translation for global team\n\nbefore: hiring translators for docs, waiting days\nafter: AI translates instantly to 12 languages\n\n$3k/month saved",
        "deployed sentiment analysis on support\n\nbefore: unhappy customers escalating unnoticed\nafter: AI flags negative sentiment for priority handling\n\nCSAT score up 31 points",
        "created personalized learning paths\n\nbefore: everyone gets same training, 40% completion\nafter: AI customizes based on role and progress\n\n87% completion rate",
        "built competitive pricing monitor\n\nbefore: checking competitor prices manually weekly\nafter: AI tracks prices across 50 competitors hourly\n\nalways competitively priced",
        "automated social proof collection\n\nbefore: manually asking happy customers for testimonials\nafter: AI identifies satisfaction, requests review at optimal time\n\n5x more testimonials",
        "implemented smart email routing\n\nbefore: emails sitting in generic inbox for hours\nafter: AI routes to right person immediately\n\nresponse time from 4 hours to 18 minutes",
        "created bug report triage system\n\nbefore: dev team reading through every bug report\nafter: AI categorizes by severity and area\n\ncritical bugs fixed 3x faster",
        "built influencer match system\n\nbefore: marketing team manually researching influencers\nafter: AI finds best-fit creators for campaigns\n\n$15k time saved per campaign",
        "automated compliance checking\n\nbefore: legal team manually reviewing every doc for compliance\nafter: AI flags potential issues\n\n70% fewer escalations",
        "deployed demand forecasting for manufacturing\n\nbefore: producing based on gut feel\nafter: AI predicts demand 8 weeks out\n\ninventory costs down 25%",
        "created automated A/B test analysis\n\nbefore: marketer running test, waiting, manually analyzing\nafter: AI determines winner, implements automatically\n\ntest velocity 5x faster",
        "built smart notification system\n\nbefore: team drowning in alerts, missing important ones\nafter: AI learns what matters to each person\n\nalert fatigue eliminated",
        "automated financial reporting\n\nbefore: accountant spending 3 days on month-end close\nafter: AI generates reports automatically\n\n4 hours to review",
        "implemented predictive maintenance\n\nbefore: equipment failing unexpectedly\nafter: AI predicts failure 2 weeks in advance\n\ndowntime reduced 60%",
        "created content performance predictor\n\nbefore: publishing content, hoping it performs\nafter: AI predicts engagement before publishing\n\nfocus time on high-performers",
        "built talent matching system\n\nbefore: managers guessing at best person for project\nafter: AI matches based on skills, availability, past performance\n\nproject success rate up 40%"
    ]

    # Category 3: Value Bombs/Tips (60 tweets)
    value_bombs = [
        "3 AI mistakes costing you money:\n\n1. buying enterprise when basic tier works\n2. building custom when API integration solves it\n3. automating broken processes instead of fixing them first",
        "the AI stack that actually works for small businesses:\n\n• Claude for text/analysis\n• Zapier for connections\n• Airtable for data\n• Nothing else\n\ntotal cost: under $100/month",
        "how to know if AI can help your business:\n\nask: 'do we do the same task more than 10 times/month?'\n\nif yes → automate it\nif no → do it manually\n\ndon't overthink it",
        "5 prompts that actually work for business:\n\n1. 'analyze this data and tell me the 3 most important insights'\n2. 'rewrite this for [audience] reading level'\n3. 'what questions would a skeptic ask about this?'\n4. 'summarize in 3 bullets: what, why, next steps'\n5. 'what am I missing here?'",
        "the AI tools I actually use daily:\n\n• Claude for thinking through problems\n• Zapier for connecting stuff\n• Notion AI for cleaning up notes\n\neverything else is noise",
        "want to test if AI can help your business?\n\ntake your most repetitive task\ntime how long it takes\ngive AI the same task\n\nif AI is faster and good enough quality → automate\nif not → keep doing it yourself",
        "biggest AI ROI for most businesses:\n\n1. email management (2-3 hours saved daily)\n2. meeting summaries (1-2 hours)\n3. first-draft content (3-4 hours)\n\nstart there, not with fancy agents",
        "how to write prompts that actually work:\n\n1. give context\n2. be specific about format\n3. show an example\n4. say what NOT to do\n\nstop writing 'make this better' and wondering why results suck",
        "free AI tools better than paid alternatives:\n\n• Claude free tier > most $50/mo writing tools\n• Zapier free plan > basic automation needs\n• Google's NotebookLM > most research assistants\n\nsave your money",
        "3 questions before buying any AI tool:\n\n1. what specific problem does this solve?\n2. can I build this with existing tools + APIs?\n3. what happens if this company shuts down?\n\nmost 'AI solutions' fail these tests",
        "the difference between AI that works and AI that doesn't:\n\nworks: solves one specific problem really well\ndoesn't work: tries to do everything, does nothing great\n\nstop looking for Swiss Army knives",
        "AI automation checklist:\n\n☐ task is repetitive\n☐ has clear rules/patterns\n☐ done more than 5x/week\n☐ doesn't require human judgment\n☐ failure isn't catastrophic\n\nall 5 checked? automate it",
        "how to calculate AI ROI:\n\nhours saved per week × hourly cost = weekly savings\nweekly savings × 50 weeks = annual value\n\nif annual value > 10x the tool cost, it's worth it",
        "realistic AI implementation timeline:\n\n• day 1: identify task to automate\n• day 2-3: test solution\n• day 4-5: refine and deploy\n• week 2+: monitor and adjust\n\nif someone quotes 3 months, run",
        "the AI learning path nobody talks about:\n\n1. learn to use ChatGPT/Claude well (1 week)\n2. learn basic API calls (1 week)\n3. learn Zapier connections (2 days)\n\nthat's it. you don't need a CS degree",
        "signs an AI consultant is overcharging you:\n\n• talks about 'training custom models'\n• quotes 6+ month timeline\n• can't explain solution in plain English\n• wants huge upfront payment\n\nget a second opinion",
        "AI tools by priority for startups:\n\n1. email/calendar management (saves founder time)\n2. customer support triage (scales without headcount)\n3. content generation (maintains marketing presence)\n\neverything else is nice-to-have",
        "how to start with AI if you're not technical:\n\nweek 1: spend 30min/day just using ChatGPT for work tasks\nweek 2: try Zapier for one simple automation\nweek 3: connect the two\n\ncongrats, you're doing AI automation",
        "the AI cost breakdown nobody shows:\n\n• tool subscription: $50/month\n• API calls: $20/month\n• time to set up: 5 hours\n• time to maintain: 30min/month\n\nplan for this, not just the subscription fee",
        "3 AI use cases with immediate ROI:\n\n1. meeting notes → action items (saves 5+ hours/week)\n2. customer emails → categorized/routed (saves 3+ hours/day)\n3. long docs → summary bullets (saves 2+ hours/day)",
        "the only AI metrics that matter:\n\n• time saved\n• money saved\n• revenue generated\n\neverything else (tokens used, model version, etc) is vanity",
        "AI prompt framework that works:\n\n'You are a [role]. I need [specific output]. Context: [relevant info]. Format: [desired structure]. Don't [common mistakes].'",
        "how to pitch AI projects to your boss:\n\n❌ 'we should try AI'\n✓ 'this task costs us X hours/week, AI can cut that to Y hours, here's the 2-day test plan'\n\nbe specific",
        "AI tools to avoid:\n\n• anything requiring 'training period'\n• tools that won't show pricing\n• solutions that need dedicated IT support\n• platforms with vendor lock-in\n\nkeep it simple",
        "the 80/20 of AI for business:\n\n80% of value comes from:\n• good prompts\n• simple automations\n• basic API integrations\n\nyou don't need the complex 20%",
        "5 signs your business is ready for AI:\n\n1. you have repetitive tasks\n2. you have consistent processes\n3. you have data to work with\n4. you have budget for tools\n5. you're willing to iterate\n\nthat's it",
        "AI implementation mistakes I see:\n\n1. automating before documenting the process\n2. no testing phase\n3. no human oversight\n4. no feedback loop\n5. trying to automate everything at once",
        "the AI prompt library every business needs:\n\n• summarize this\n• find errors in this\n• rewrite for [audience]\n• extract key points\n• what's missing?\n\ncovers 90% of use cases",
        "how to evaluate AI tools:\n\nday 1: free trial, test with real work\nday 2: if it saved time, calculate ROI\nday 3: if ROI > 5x cost, buy it\n\nstop overthinking",
        "realistic expectations for AI:\n\n✓ can: handle repetitive tasks, first drafts, data analysis\n✗ can't: replace human judgment, handle edge cases, fix bad processes\n\nuse accordingly"
    ]

    # Add all with proper formatting
    tweet_id = 1

    for content in hot_takes[:60]:
        tweets.append({
            "id": tweet_id,
            "content": content,
            "type": "hot_take",
            "viral_potential": "high" if tweet_id % 3 == 0 else "medium",
            "category": "hot_take"
        })
        tweet_id += 1

    for content in before_after[:50]:
        tweets.append({
            "id": tweet_id,
            "content": content,
            "type": "before_after",
            "viral_potential": "high",
            "category": "case_study"
        })
        tweet_id += 1

    for content in value_bombs[:30]:
        tweets.append({
            "id": tweet_id,
            "content": content,
            "type": "value_bomb",
            "viral_potential": "high" if tweet_id % 2 == 0 else "medium",
            "category": "educational"
        })
        tweet_id += 1

    # Category 4: Questions (30 tweets)
    questions = [
        "quick poll: what's eating most of your time?\n\n1. emails\n2. meetings\n3. admin tasks\n4. customer support\n\ncurious what people would automate first",
        "founders: what's the one task you wish you could delegate but can't afford to hire for yet?",
        "which AI breakthrough would actually help your business?\n\n• better conversation\n• faster processing\n• cheaper pricing\n• easier setup",
        "real question: is your team actually using the AI tools you're paying for, or are they just sitting there?",
        "what's the most repetitive part of your job that you're convinced can't be automated?",
        "if you could automate one thing tomorrow, what would it be?",
        "honest question: how many AI tool subscriptions are you paying for but not using?",
        "what's the AI feature you thought you needed but never actually use?",
        "which sounds more valuable:\n\n• tool that saves 1 hour/day\n• tool that makes $1k extra/month\n\nsame cost for both",
        "what's stopping you from trying AI automation? (honest answers only)",
        "if AI could handle your 3 most hated tasks, what would they be?",
        "small business owners: what's the task you're doing manually that you KNOW could be automated?",
        "which would help your business more:\n\n1. faster customer response\n2. better lead quality\n3. less time in admin\n4. more content output",
        "what's the worst AI tool you've paid for and why?",
        "real talk: what AI use case actually sounds useful vs what sounds like hype?",
        "what's your biggest hesitation about implementing AI in your workflow?",
        "if you had to cut 10 hours/week from your schedule, which tasks would you eliminate?",
        "founders: what's the one process in your business that's held together with duct tape and hope?",
        "which pricing model for AI tools makes more sense:\n\n• flat monthly fee\n• pay per use\n• one-time payment",
        "what's a task you're doing manually that everyone assumes you've automated by now?",
        "honest question: do you trust AI to handle customer communication?",
        "what would make you switch from your current tools to an AI alternative?",
        "if AI agencies weren't so expensive, what would you hire one to build first?",
        "what's the AI demo that impressed you but you never actually bought?",
        "which is more frustrating:\n\n• tool that's powerful but complicated\n• tool that's simple but limited",
        "what task do you do daily that makes you think 'there HAS to be a better way'?",
        "real question: would you rather save 10 hours/week or make an extra $2k/month?",
        "what's the AI tool everyone recommends that you tried and hated?",
        "if you could only automate one department in your business, which one and why?",
        "what's your most time-consuming task that you're pretty sure can't be automated?"
    ]

    for content in questions[:30]:
        tweets.append({
            "id": tweet_id,
            "content": content,
            "type": "question",
            "viral_potential": "medium",
            "category": "engagement"
        })
        tweet_id += 1

    # Category 5: Contrarian Takes (40 tweets)
    contrarian = [
        "unpopular opinion: AI won't kill jobs, it'll kill the excuses people make for being unproductive",
        "controversial: most businesses should fix their processes before adding AI. AI just makes bad processes faster",
        "hot take: if you can't explain your AI solution to a 10-year-old, you don't understand it well enough to sell it",
        "unpopular: the best AI implementation is the one your users don't even know is AI",
        "controversial take: 90% of 'AI consultants' are just people who learned to use ChatGPT last month",
        "unpopular opinion: custom AI models are almost always a waste of money. learn to prompt well instead",
        "hot take: AI agents aren't the future, invisible AI doing boring tasks in the background is",
        "controversial: if your AI needs human review for every output, you built it wrong",
        "unpopular take: most AI tools are solutions looking for problems, not solving actual pain points",
        "hot take: the AI companies that win will be boring ones solving unsexy problems, not the ones making flashy demos",
        "controversial opinion: paying $10k for AI consulting is usually paying for someone to Google stuff for you",
        "unpopular: AI making you 10% faster at bad strategy is worse than doing good strategy slowly",
        "hot take: if you're using AI to write your tweets, you should probably just say less",
        "controversial: businesses that succeed with AI aren't the early adopters, they're the ones who implement well",
        "unpopular opinion: most AI failures aren't technology problems, they're change management problems",
        "hot take: AI democratization is creating more noise, not more value. quality over quantity",
        "controversial: the best AI projects are the ones that take 1 day to build, not 6 months",
        "unpopular take: AI won't replace you, but someone using AI better than you will",
        "hot take: if your AI pitch deck is 40 slides, you don't have a clear value prop",
        "controversial opinion: most 'AI-powered' products would work just as well with basic automation",
        "unpopular: teaching AI to sound more human is missing the point. humans should learn what AI is good at",
        "hot take: the AI skills gap isn't coding, it's critical thinking and knowing what to automate",
        "controversial: companies spending millions on AI while ignoring basic automation are doing it for PR",
        "unpopular opinion: AI that requires training data is already obsolete. foundation models won",
        "hot take: if you need a data scientist on staff to use your AI product, it's not a product, it's consulting",
        "controversial: most AI ethics concerns are covering for 'I don't want to learn new technology'",
        "unpopular take: AI making content creation easy means most content is now worthless. distribution is the new game",
        "hot take: the best use of AI is doing tasks you hate, not doing creative work you enjoy",
        "controversial opinion: businesses using AI to cut costs but not improve customer experience will lose",
        "unpopular: AI agents working autonomously is a liability, not a feature. humans should stay in the loop",
        "hot take: if your AI can't show ROI in 30 days, it's not solving a real problem",
        "controversial: the AI revolution is overhyped. it's just faster automation, not magic",
        "unpopular opinion: most people don't need AI, they need to learn keyboard shortcuts and actually use the tools they have",
        "hot take: AI companies pivoting to 'AI' are like restaurants adding 'organic' to their name",
        "controversial: the best AI products are the ones that don't require reading documentation",
        "unpopular take: AI can write code but shouldn't. debugging AI-written code is worse than writing it yourself",
        "hot take: if you're proud your AI uses 'advanced reasoning', you're admitting your prompts are bad",
        "controversial opinion: most AI automation should take hours to set up, not months. if it's taking months, you're overengineering",
        "unpopular: AI-generated art isn't the problem, people with no taste using it everywhere is",
        "hot take: the future isn't AGI, it's really good narrow AI that actually works reliably"
    ]

    for content in contrarian[:40]:
        tweets.append({
            "id": tweet_id,
            "content": content,
            "type": "contrarian",
            "viral_potential": "high",
            "category": "thought_leadership"
        })
        tweet_id += 1

    # Category 6: Personal Stories/Lessons (40 tweets)
    stories = [
        "learned this the hard way: clients don't care about your tech stack, they care about the problem you solved and how fast you did it",
        "built an AI solution that took 3 months and $50k. client used it twice then went back to their spreadsheet. expensive lesson in not validating first",
        "best business decision last year: saying no to 'exciting' AI projects that didn't have clear ROI. boring profitable work > cool unprofitable work",
        "made $100k last year just teaching people how to use tools they already pay for. market for AI expertise is bigger than market for AI products",
        "spent 6 months building a perfect AI system. competitor shipped a 'good enough' version in 2 weeks and won the market. speed > perfection",
        "client wanted custom AI chatbot. convinced them to try Claude + Zapier first. saved them $80k and solved their problem. sometimes the best solution is not building",
        "biggest aha moment: stopped selling 'AI automation' and started selling 'get 10 hours back per week'. same service, 5x more sales",
        "turned down a $100k AI project because I knew it would fail. client built it anyway with someone else. failed in 3 months. trust your gut",
        "used to think I needed to learn ML and Python. turns out knowing business problems + basic APIs = more valuable than technical depth",
        "lost a client because I was too honest about them not needing AI yet. they hired someone else, wasted $50k, came back. honesty pays long-term",
        "automated my own agency's operations before selling to clients. went from 60hr weeks to 25hr weeks, same revenue. eat your own dog food",
        "raised prices 3x, got more clients. premium positioning in AI space works because everyone's afraid of choosing wrong",
        "built 20 AI demos last year. 1 made money. the boring one solving email overload, not the sexy ChatGPT wrapper",
        "client said 'we want to be AI-first'. I asked 'why?' they had no answer. saved them from expensive mistake by asking obvious questions",
        "made more money with Zapier + Claude than any custom ML project. simple solutions, happy clients, predictable outcomes",
        "thought I needed technical cofounder. turns out I just needed to learn API documentation and basic Python. saved 50% equity",
        "stopped competing on tech specs, started competing on implementation speed. went from 10% close rate to 60%",
        "best ROI on learning: spent $0 reading API docs > spent $5k on AI courses. practical beats theoretical",
        "client had 'AI strategy consultant' billing $20k/month for decks. I built working prototype in 2 days. action beats strategy",
        "realized most clients don't want AI, they want their problems solved. rebranded from 'AI agency' to 'automation agency', revenue doubled",
        "used to build complex solutions to prove I was smart. now I build simple solutions to prove I understand the problem. clients prefer the latter",
        "lost 3 months and $30k building an AI product nobody wanted. now I validate with 1-week MVP before building anything. expensive lesson",
        "thought AI would replace my job. instead it eliminated the parts I hated and let me focus on creative work. best case scenario",
        "client wanted everything automated. I automated one task. they were happy. scope creep kills projects, focus wins",
        "made the mistake of over-delivering. built 10 features, client used 2. now I ship minimum viable solution first, add later if needed",
        "spent 2 years building technical skills. should've spent 6 months on technical, 18 months on sales. revenue comes from customers, not capabilities",
        "best client feedback: 'I forget your tool is even there, it just works'. invisible AI > impressive AI",
        "raised my rates, clients took me more seriously. cheap AI consulting = amateur in client's mind",
        "used to work with everyone. now I only work with clients who have budget and urgency. 3x less work, 5x more revenue",
        "automated client's process they insisted couldn't be automated. turned out they just never actually tried. question assumptions",
        "lost deal to competitor with better marketing but worse product. learned: distribution > product. painful but true",
        "built AI tool for myself, accidentally created a product. scratching your own itch is the best product strategy",
        "client ghosted after I delivered exactly what they asked for. realized I should've delivered what they needed, not what they said. learn to translate",
        "spent $10k on tools last year. made money on $100 worth of them. cheaper ≠ worse, expensive ≠ better",
        "stopped trying to be impressive in sales calls, started asking questions about their problems. close rate tripled",
        "automated a client's job partially. they got promoted for efficiency gains. AI makes good people look great",
        "tried to sell to enterprises. sales cycles killed me. now I sell to SMBs with short cycles and fast decisions. cash flow = freedom",
        "thought I needed VC funding to scale. bootstrapped to $500k/year instead. profitability > growth for happiness",
        "client wanted bleeding-edge AI. I used 2-year-old technology that actually works. reliability beats innovation for businesses",
        "made more from 5 happy clients referring me than from all my marketing combined. do great work, ask for intros, repeat"
    ]

    for content in stories[:40]:
        tweets.append({
            "id": tweet_id,
            "content": content,
            "type": "story",
            "viral_potential": "high" if tweet_id % 2 == 0 else "medium",
            "category": "personal"
        })
        tweet_id += 1

    # Category 7: Quick Tips (50 tweets)
    quick_tips = [
        "best Claude prompt I use daily:\n\n'be concise, be direct, skip the preamble'\n\nadds this to every prompt, saves scrolling through fluff",
        "if your AI output sounds robotic, add this to your prompt:\n\n'write like you're explaining to a colleague over coffee'",
        "Zapier tip: start with 2-step zaps. resist the urge to build complex workflows. simple = maintainable",
        "testing AI solutions:\n\nrun it on 10 real examples before deploying\n\nif 8+ work perfectly, ship it\nif not, refine",
        "free AI stack:\n• Claude (better than ChatGPT for business)\n• Zapier free tier\n• Google Sheets\n• 15 minutes of setup\n\nstop overthinking",
        "want AI to stop writing like AI?\n\nadd to prompt: 'use short sentences. vary length. no jargon.'",
        "best way to learn AI: take your most annoying task, spend 1 hour trying to automate it. repeat daily",
        "prompt tip: say what NOT to do\n\n'don't apologize, don't restate the question, don't add disclaimers'\n\ngets better outputs",
        "AI tool evaluation:\n\nday 1: try it\nday 2: calculate time saved\nday 3: decide\n\nstop overthinking tools",
        "building AI workflows:\n\nstep 1: document current process\nstep 2: identify repetitive parts\nstep 3: automate those only\n\ndon't automate everything",
        "Claude vs ChatGPT:\n\nClaude: better for business analysis, less preachy\nChatGPT: better for brainstorming, more creative\n\nuse both",
        "AI prompt structure:\n\n[role] + [task] + [context] + [format] + [constraints]\n\nexample: 'you're a marketing analyst. analyze this data. we're B2B SaaS. give 3 bullets. be specific.'",
        "fastest AI ROI: automate your own work first, then sell that solution to others",
        "stop asking AI to 'make it better'. say exactly what better means: shorter, more specific, different tone, etc",
        "AI tools worth paying for:\n\n1. Claude Pro ($20/mo) — unlimited use\n2. Zapier ($20/mo) — real automation\n\neverything else is optional",
        "when AI output is wrong:\n\nadd more context to your prompt\nshow an example\nspecify the format\n\n95% of 'bad AI' is bad prompting",
        "best meeting use of AI: record → transcribe → extract action items → email to team\n\nmeetings become useful again",
        "AI implementation rule: if it takes more than 1 week to set up, you're overcomplicating it",
        "want better AI outputs? write prompts like you're briefing a smart junior employee, not commanding a robot",
        "Zapier alternative if you're technical: n8n (self-hosted, free). 2 hours learning curve, worth it",
        "AI content strategy: use AI for first draft, human for final polish. 10x faster than starting from scratch",
        "testing prompt quality: run it 5 times. if outputs are consistent and good, your prompt works",
        "stop using AI to generate everything. use it to handle the boring parts so you can focus on creative decisions",
        "client asked for AI chatbot. I asked 'what problem are you solving?' they didn't know. start with problem, not solution",
        "AI email management: sort into 4 folders: urgent, reply needed, fyi, delete. game changer",
        "measuring AI success: time saved × hourly rate = value created. if positive, keep it",
        "best AI use case: summarizing long docs into action items. saves 5-10 hours/week easy",
        "prompt engineering isn't complex: be specific, give examples, say what you don't want. that's 90% of it",
        "AI workflow tip: start with manual process, automate one step per week. gradual beats trying to automate everything at once",
        "best question for AI vendors: 'show me someone using this successfully'. if they can't, walk away",
        "stop trying to use AI for creative strategy. use it for execution. humans think, AI does",
        "AI content tip: generate 10 options, pick best 1, edit it. faster than trying to write perfect prompt",
        "when to NOT use AI: anything requiring nuance, empathy, or judgment calls. keep humans in the loop",
        "AI prompts to save:\n\n• tldr this\n• make it shorter\n• explain like I'm not technical\n• what questions would someone ask?\n• what's the action item?",
        "Zapier trigger tip: start with 'new row in spreadsheet'. simplest way to kick off workflows",
        "AI debugging: if output is wrong, ask AI 'what info would help you answer this better?'. it'll tell you",
        "stop using AI to sound smart. use it to be clear. clarity > complexity",
        "best automation to start with: email categorization. takes 30min to set up, saves 1hr/day",
        "AI team tip: train everyone on prompts, not on tools. prompting is the skill, tools are interchangeable",
        "want AI that sounds human? add typos and casual language to your prompts. 'write like you're texting'",
        "measuring AI projects: set success metric BEFORE building. 'reduces time by X' or 'saves $Y'. then measure",
        "AI implementation strategy: crawl (1 task), walk (1 workflow), run (full automation). don't skip steps",
        "best AI learning resource: YouTube + actually building stuff. courses are overkill",
        "prompt tip for analysis: 'assume I know nothing, explain your reasoning'\n\ngets better explanations",
        "AI pricing strategy: charge for value delivered, not hours spent. AI makes you faster, don't punish yourself",
        "stop asking 'can AI do this?' and start asking 'should AI do this?'. not everything should be automated",
        "AI tool fatigue fix: pick 2 tools max, master them. being great with 2 beats being mediocre with 10",
        "best AI workflow: human plans → AI executes → human reviews. that's the pattern",
        "prompt efficiency: save your good prompts in a doc. 10 great prompts cover 80% of use cases",
        "AI automation priority: automate most frequent tasks first, not hardest. frequency × time saved = priority score"
    ]

    for content in quick_tips:
        tweets.append({
            "id": tweet_id,
            "content": content,
            "type": "tip",
            "viral_potential": "medium",
            "category": "tactical"
        })
        tweet_id += 1

    return tweets

def save_library(tweets):
    """Save tweet library to file"""
    output_dir = Path('.tmp')
    output_dir.mkdir(exist_ok=True)

    library = {
        'generated_date': datetime.now().isoformat(),
        'total_tweets': len(tweets),
        'by_category': {
            'hot_take': len([t for t in tweets if t['type'] == 'hot_take']),
            'before_after': len([t for t in tweets if t['type'] == 'before_after']),
            'value_bomb': len([t for t in tweets if t['type'] == 'value_bomb']),
            'question': len([t for t in tweets if t['type'] == 'question']),
            'contrarian': len([t for t in tweets if t['type'] == 'contrarian']),
            'story': len([t for t in tweets if t['type'] == 'story']),
            'tip': len([t for t in tweets if t['type'] == 'tip'])
        },
        'tweets': tweets
    }

    with open(output_dir / 'tweet_library.json', 'w', encoding='utf-8') as f:
        json.dump(library, f, indent=2, ensure_ascii=False)

    print(f"\n[OK] Generated {len(tweets)} tweets")
    print(f"[OK] Saved to .tmp/tweet_library.json")
    print(f"\nBreakdown:")
    for category, count in library['by_category'].items():
        print(f"  • {category}: {count} tweets")

def main():
    print("Generating bulk tweet library...\n")
    tweets = generate_tweet_library()
    save_library(tweets)
    print("\n" + "="*60)
    print("Ready to use! Pick any tweet from .tmp/tweet_library.json")
    print("="*60)

if __name__ == "__main__":
    main()
