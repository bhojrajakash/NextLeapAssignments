# SBI Mutual Fund FAQ Assistant

## Project Overview
A facts-only FAQ assistant for SBI Mutual Funds built using Claude.ai Projects with RAG (Retrieval-Augmented Generation) capabilities. No investment advice provided.

## Product Selected
**INDMoney** (as per Milestone 1 requirement)

## Scope
**AMC:** SBI Mutual Fund  
**Schemes Covered:**
1. SBI Bluechip Fund (Large Cap Equity)
2. SBI Flexicap Fund (Flexi Cap Equity)
3. SBI Long Term Equity Fund (ELSS - Tax Saving)

## Features
- Answers factual queries about:
  - Expense ratios (Regular vs Direct plans)
  - Exit loads and charges
  - Minimum SIP amounts
  - Minimum lumpsum investments
  - Lock-in periods (ELSS 3-year lock-in)
  - Riskometer ratings
  - Benchmark indices
  - How to download statements
- Every answer includes one source citation
- Politely refuses investment advice questions
- Transparent about source update dates

## Knowledge Base
**Total Sources:** [Put your number - should be 15+]

**Source Types:**
- SBI Mutual Fund official scheme pages (3)
- Factsheets (3 PDFs)
- Key Information Memorandums (KIMs)
- SBI MF FAQ and informational pages
- AMFI investor education resources
- SEBI regulatory guidelines

Complete source list: See `Source_List.csv`

## Technical Implementation
**Platform:** Claude.ai Projects  
**RAG Approach:** Built-in document upload + custom instruction prompting  
**LLM:** Claude Sonnet 4.5  
**No external hosting required**

## Setup Instructions
1. Access the Claude.ai project (link provided)
2. Documents are pre-uploaded to project knowledge base
3. Custom instructions handle fact-only responses and citation formatting
4. Simply ask questions in natural language

## Sample Questions
✅ Factual (Will Answer):
- "What is the expense ratio of SBI Bluechip Fund?"
- "What is the ELSS lock-in period?"
- "Minimum SIP for SBI Flexicap?"
- "How do I download my capital gains statement?"

❌ Advice (Will Refuse):
- "Should I invest in SBI ELSS?"
- "Which fund is better?"
- "Will this give good returns?"

## Limitations & Constraints
- **Facts only** - No investment recommendations or advice
- **Limited scope** - Only 3 SBI schemes covered
- **Public sources only** - No proprietary or backend data
- **No PII** - Does not collect PAN, Aadhaar, account numbers, OTP, email, or phone
- **No performance claims** - Does not calculate or compare returns
- **Sources dated** - Information current as of November 2025

## Disclaimer
⚠️ **FACTS ONLY - NO INVESTMENT ADVICE**

This assistant provides factual information only and does not constitute investment advice, financial planning, or recommendations. It does not consider individual financial situations, risk profiles, or investment goals.

For personalized investment guidance, please consult:
- SEBI-registered Investment Advisors
- Certified Financial Planners
- Tax professionals for tax-related queries

Mutual fund investments are subject to market risks. Please read all scheme-related documents carefully before investing.

## Deliverables Included
1. ✅ Working prototype (Claude.ai Project)
2. ✅ Source list (Source_List.csv with 15+ URLs)
3. ✅ README.md (this file)
4. ✅ Sample Q&A file (10 queries with answers)
5. ✅ Disclaimer snippet
6. ✅ Demo video (2-3 minutes)

## Skills Demonstrated
- **W1 - Thinking Like a Model:** Identifying exact facts requested, deciding when to answer vs refuse
- **W2 - LLMs & Prompting:** Instruction design, concise phrasing, polite refusals, citation formatting
- **W3 - RAGs:** Small-corpus retrieval with accurate citations from official sources

## Access
**Project Link:** [Your Claude.ai project share link - see instructions below]

## Author
[Your Name]  
Product Manager Fellowship - Milestone 1  
Date: November 17, 2025
