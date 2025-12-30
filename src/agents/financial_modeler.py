"""
Financial Modeler Agent - Business Analysis Phase
Generates comprehensive financial models, unit economics, and revenue projections.
"""

from typing import Dict, Any, Tuple
from ..ai_models import GeminiClient
from ..helpers import BMAdHelpers, get_standard_prompt_suffix
from ..agent_state import AgentState, add_status_message


class FinancialModelerAgent:
    """
    Financial Modeler - Business Analysis Phase
    
    Responsibilities:
    - Generate revenue projections (Year 1-3)
    - Calculate unit economics (CAC, LTV, LTV:CAC ratio)
    - Create cost structure analysis
    - Calculate burn rate and runway
    - Perform break-even analysis
    
    Output: financial_model.md
    """
    
    def __init__(self, api_key: str, model_name: str = "gemini-2.5-flash"):
        """Initialize Financial Modeler agent"""
        self.api_key = api_key
        self.model_name = model_name
        self.helpers = BMAdHelpers()
        self.llm = GeminiClient(api_key)
    
    def generate_financial_model(
        self, 
        state: AgentState,
        product_brief: str = "",
        prd: str = ""
    ) -> str:
        """
        Generate comprehensive financial model.
        
        Args:
            state: Agent state
            product_brief: Product brief markdown
            prd: PRD markdown
        
        Returns:
            financial_model_markdown
        """
        idea = state["idea"]
        add_status_message(state, "Financial Modeler: Creating financial projections...")
        
        # Research pricing and market benchmarks
        research_prompt = f"""
{self.helpers.get_role_definition("market_analyst")}

**Objective:**
Research financial benchmarks for similar products using Google Search:
1. Typical pricing models and tiers for this industry
2. Customer Acquisition Cost (CAC) benchmarks
3. Lifetime Value (LTV) estimates
4. Churn rates for similar products
5. Development costs and team size benchmarks
6. Infrastructure costs (hosting, tools)

**Context:**
Startup Idea: {idea}

**Output:**
Provide detailed financial benchmarks and pricing research.
{get_standard_prompt_suffix()}
"""
        
        # Call Gemini with Grounding
        research_result = self.llm.generate_with_grounding(research_prompt, model_name=self.model_name)
        research_text = research_result["text"]
        citations = research_result.get("citations", [])
        
        add_status_message(state, f"Financial Modeler: Found {len(citations)} financial sources.")
        
        # Generate financial model
        model_prompt = f"""
You are a Financial Analyst and CFO consultant with 15+ years of experience building financial models for SaaS startups.

**Objective:**
Create a comprehensive **Financial Model** based on the research and product details provided.

**Research Data:**
{research_text}

**Product Brief:**
{product_brief[:2000] if product_brief else "Not available"}

**PRD:**
{prd[:2000] if prd else "Not available"}

**Structure:**
# Financial Model: {idea}

## 1. Executive Summary
- **Business Model:** [Subscription/Transaction/Freemium/etc.]
- **Target Revenue Year 3:** $[Amount]
- **Break-Even Point:** [Month/Quarter]
- **Funding Required:** $[Amount]

---
**Rationale:**
Explain the chosen business model and revenue targets based on market research.

**Agent Guidance:**
This financial model provides baseline assumptions. Adjust parameters based on actual market feedback during MVP validation.

---

## 2. Revenue Projections (Years 1-3)

### Assumptions
| Metric | Year 1 | Year 2 | Year 3 | Basis |
|--------|--------|--------|--------|-------|
| **Monthly Active Users (MAU)** | [Number] | [Number] | [Number] | Conservative growth based on market research |
| **Conversion Rate** | [%] | [%] | [%] | Industry benchmark |
| **Average Revenue Per User (ARPU)** | $[Amount] | $[Amount] | $[Amount] | Pricing research |
| **Churn Rate (Monthly)** | [%] | [%] | [%] | Industry average |

---
**Rationale:**
Explain the assumptions and how they're derived from research. Reference competitor data.

**Agent Guidance:**
Use these projections to inform feature prioritization. High ARPU requires premium features; high churn requires retention features.

---

### Revenue Breakdown

| Revenue Stream | Year 1 | Year 2 | Year 3 | Notes |
|----------------|--------|--------|--------|-------|
| **Subscription Revenue** | $[Amount] | $[Amount] | $[Amount] | [Tier breakdown] |
| **Transaction Fees** | $[Amount] | $[Amount] | $[Amount] | [If applicable] |
| **Add-On Services** | $[Amount] | $[Amount] | $[Amount] | [Premium features] |
| **Enterprise Plans** | $[Amount] | $[Amount] | $[Amount] | [Custom pricing] |
| **Total Revenue** | $[Amount] | $[Amount] | $[Amount] | [Sum] |

---
**Rationale:**
Explain revenue diversification strategy and why multiple streams reduce risk.

---

### Monthly Recurring Revenue (MRR) Growth

| Quarter | Year 1 MRR | Year 2 MRR | Year 3 MRR | Growth Rate |
|---------|-----------|-----------|-----------|-------------|
| **Q1** | $[Amount] | $[Amount] | $[Amount] | [%] |
| **Q2** | $[Amount] | $[Amount] | $[Amount] | [%] |
| **Q3** | $[Amount] | $[Amount] | $[Amount] | [%] |
| **Q4** | $[Amount] | $[Amount] | $[Amount] | [%] |

---

## 3. Cost Structure

### Development Costs

| Category | Year 1 | Year 2 | Year 3 | Notes |
|----------|--------|--------|--------|-------|
| **Team Salaries** | $[Amount] | $[Amount] | $[Amount] | [Team size: N engineers, N designers] |
| **Contractors** | $[Amount] | $[Amount] | $[Amount] | [Specialized skills] |
| **Development Tools** | $[Amount] | $[Amount] | $[Amount] | [IDEs, CI/CD, monitoring] |
| **Total Dev Costs** | $[Amount] | $[Amount] | $[Amount] | [Sum] |

---
**Rationale:**
Explain team size decisions based on product complexity and timeline.

---

### Infrastructure Costs

| Category | Year 1 | Year 2 | Year 3 | Notes |
|----------|--------|--------|--------|-------|
| **Cloud Hosting** | $[Amount] | $[Amount] | $[Amount] | [AWS/GCP/Azure] |
| **CDN & Storage** | $[Amount] | $[Amount] | $[Amount] | [S3, CloudFront] |
| **Database** | $[Amount] | $[Amount] | $[Amount] | [RDS, managed services] |
| **Third-Party APIs** | $[Amount] | $[Amount] | $[Amount] | [Payment, AI, maps, etc.] |
| **Total Infra Costs** | $[Amount] | $[Amount] | $[Amount] | [Sum] |

---

### Marketing & Sales Costs

| Category | Year 1 | Year 2 | Year 3 | Notes |
|----------|--------|--------|--------|-------|
| **Digital Advertising** | $[Amount] | $[Amount] | $[Amount] | [Google, Facebook, LinkedIn] |
| **Content Marketing** | $[Amount] | $[Amount] | $[Amount] | [Blog, SEO, social media] |
| **Sales Team** | $[Amount] | $[Amount] | $[Amount] | [If applicable] |
| **Marketing Tools** | $[Amount] | $[Amount] | $[Amount] | [CRM, analytics, email] |
| **Total Marketing Costs** | $[Amount] | $[Amount] | $[Amount] | [Sum] |

---

### Operating Expenses

| Category | Year 1 | Year 2 | Year 3 | Notes |
|----------|--------|--------|--------|-------|
| **Office & Admin** | $[Amount] | $[Amount] | $[Amount] | [Remote-first assumed] |
| **Legal & Accounting** | $[Amount] | $[Amount] | $[Amount] | [Incorporation, taxes, IP] |
| **Insurance** | $[Amount] | $[Amount] | $[Amount] | [Liability, D&O] |
| **Miscellaneous** | $[Amount] | $[Amount] | $[Amount] | [10% buffer] |
| **Total OpEx** | $[Amount] | $[Amount] | $[Amount] | [Sum] |

---

### Total Cost Summary

| Category | Year 1 | Year 2 | Year 3 |
|----------|--------|--------|--------|
| **Development** | $[Amount] | $[Amount] | $[Amount] |
| **Infrastructure** | $[Amount] | $[Amount] | $[Amount] |
| **Marketing & Sales** | $[Amount] | $[Amount] | $[Amount] |
| **Operating Expenses** | $[Amount] | $[Amount] | $[Amount] |
| **Total Costs** | $[Amount] | $[Amount] | $[Amount] |

---

## 4. Unit Economics

### Customer Acquisition Cost (CAC)

| Metric | Year 1 | Year 2 | Year 3 | Calculation |
|--------|--------|--------|--------|-------------|
| **Total Marketing Spend** | $[Amount] | $[Amount] | $[Amount] | [From above] |
| **New Customers Acquired** | [Number] | [Number] | [Number] | [Conversion funnel] |
| **CAC** | $[Amount] | $[Amount] | $[Amount] | Marketing Spend / New Customers |

---
**Rationale:**
Explain CAC trajectory. Should decrease over time due to marketing efficiency and word-of-mouth.

---

### Lifetime Value (LTV)

| Metric | Year 1 | Year 2 | Year 3 | Calculation |
|--------|--------|--------|--------|-------------|
| **ARPU (Monthly)** | $[Amount] | $[Amount] | $[Amount] | [From above] |
| **Avg Customer Lifespan (Months)** | [Number] | [Number] | [Number] | 1 / Churn Rate |
| **Gross Margin** | [%] | [%] | [%] | (Revenue - COGS) / Revenue |
| **LTV** | $[Amount] | $[Amount] | $[Amount] | ARPU × Lifespan × Margin |

---

### LTV:CAC Ratio

| Metric | Year 1 | Year 2 | Year 3 | Target |
|--------|--------|--------|--------|--------|
| **LTV:CAC Ratio** | [Ratio] | [Ratio] | [Ratio] | **3:1 minimum** |

---
**Rationale:**
Explain why LTV:CAC ratio is critical. < 3:1 means unsustainable growth. > 5:1 means underinvesting in marketing.

**Agent Guidance:**
If LTV:CAC < 3:1, prioritize retention features to reduce churn. If > 5:1, increase marketing spend to accelerate growth.

---

### Payback Period

| Metric | Year 1 | Year 2 | Year 3 | Target |
|--------|--------|--------|--------|--------|
| **Months to Recover CAC** | [Months] | [Months] | [Months] | **< 12 months** |

---

## 5. Burn Rate & Runway

### Cash Flow Analysis

| Quarter | Revenue | Costs | Net Cash Flow | Cumulative Cash |
|---------|---------|-------|---------------|-----------------|
| **Q1 Year 1** | $[Amount] | $[Amount] | $[Amount] | $[Amount] |
| **Q2 Year 1** | $[Amount] | $[Amount] | $[Amount] | $[Amount] |
| **Q3 Year 1** | $[Amount] | $[Amount] | $[Amount] | $[Amount] |
| **Q4 Year 1** | $[Amount] | $[Amount] | $[Amount] | $[Amount] |
| **Q1 Year 2** | $[Amount] | $[Amount] | $[Amount] | $[Amount] |
| **Q2 Year 2** | $[Amount] | $[Amount] | $[Amount] | $[Amount] |

---

### Funding Requirements

| Metric | Amount | Timing | Purpose |
|--------|--------|--------|---------|
| **Seed Funding** | $[Amount] | Pre-launch | Product development, initial marketing |
| **Series A** | $[Amount] | Month [N] | Scale marketing, expand team |
| **Total Funding Required** | $[Amount] | - | - |

---
**Rationale:**
Explain funding strategy. Bootstrap vs. VC-backed. Milestones required before each round.

**Agent Guidance:**
Use these milestones to define MVP scope. Focus on features that demonstrate product-market fit for investors.

---

### Runway Analysis

| Scenario | Monthly Burn Rate | Runway (Months) | Notes |
|----------|------------------|-----------------|-------|
| **Conservative** | $[Amount] | [Months] | Minimal marketing spend |
| **Base Case** | $[Amount] | [Months] | Planned budget |
| **Aggressive** | $[Amount] | [Months] | Accelerated growth |

---

## 6. Break-Even Analysis

### Break-Even Calculation

| Metric | Value | Notes |
|--------|-------|-------|
| **Fixed Costs (Monthly)** | $[Amount] | Team, tools, office |
| **Variable Costs (Per User)** | $[Amount] | Hosting, support, transaction fees |
| **Revenue Per User (Monthly)** | $[Amount] | ARPU |
| **Contribution Margin** | $[Amount] | Revenue - Variable Costs |
| **Break-Even Customers** | [Number] | Fixed Costs / Contribution Margin |
| **Break-Even MRR** | $[Amount] | Break-Even Customers × ARPU |
| **Break-Even Timeline** | [Month/Quarter] | Based on growth projections |

---
**Rationale:**
Explain path to profitability. Compare to industry benchmarks for time to break-even.

---

## 7. Sensitivity Analysis

### Key Assumptions Impact

| Variable | Base Case | Pessimistic (-20%) | Optimistic (+20%) | Impact on Break-Even |
|----------|-----------|-------------------|-------------------|---------------------|
| **Conversion Rate** | [%] | [%] | [%] | [+/- Months] |
| **ARPU** | $[Amount] | $[Amount] | $[Amount] | [+/- Months] |
| **Churn Rate** | [%] | [%] | [%] | [+/- Months] |
| **CAC** | $[Amount] | $[Amount] | $[Amount] | [+/- Months] |

---
**Rationale:**
Show which variables have the highest impact on success. Focus on optimizing high-impact metrics.

**Agent Guidance:**
Use sensitivity analysis to prioritize features. High-impact variables (e.g., churn) require more investment in relevant features (e.g., onboarding, engagement).

---

## 8. Financial Metrics Dashboard

### Key Performance Indicators (KPIs)

| KPI | Target | Measurement | Frequency |
|-----|--------|-------------|-----------|
| **MRR Growth Rate** | [%] per month | (Current MRR - Previous MRR) / Previous MRR | Monthly |
| **CAC** | < $[Amount] | Marketing Spend / New Customers | Monthly |
| **LTV** | > $[Amount] | ARPU × Lifespan × Margin | Quarterly |
| **LTV:CAC Ratio** | > 3:1 | LTV / CAC | Quarterly |
| **Churn Rate** | < [%] | Lost Customers / Total Customers | Monthly |
| **Gross Margin** | > [%] | (Revenue - COGS) / Revenue | Monthly |
| **Burn Rate** | $[Amount] | Monthly expenses | Monthly |
| **Runway** | > [Months] | Cash Balance / Burn Rate | Monthly |

---

## 9. Investor-Ready Summary

### Investment Highlights
- **Market Opportunity:** $[TAM], growing at [%] CAGR
- **Business Model:** [Description]
- **Revenue Year 3:** $[Amount]
- **Break-Even:** [Quarter/Month]
- **LTV:CAC Ratio:** [Ratio] by Year 2
- **Funding Ask:** $[Amount] for [Milestones]

### Use of Funds
| Category | Amount | % of Total | Purpose |
|----------|--------|-----------|---------|
| **Product Development** | $[Amount] | [%] | MVP + core features |
| **Marketing & Sales** | $[Amount] | [%] | Customer acquisition |
| **Operations** | $[Amount] | [%] | Team, legal, admin |
| **Buffer** | $[Amount] | [%] | Contingency |
| **Total** | $[Amount] | 100% | - |

---

## 10. Risk Factors & Mitigation

| Risk | Impact | Probability | Mitigation Strategy |
|------|--------|-------------|-------------------|
| **Lower conversion rate** | High | Medium | A/B test onboarding, improve UX |
| **Higher churn** | High | Medium | Build retention features, customer success |
| **CAC inflation** | Medium | High | Diversify channels, optimize SEO |
| **Delayed revenue** | Medium | Medium | Extend runway, reduce burn |
| **Competition** | High | High | Focus on differentiation, network effects |

---
**Agent Guidance:**
Use this risk assessment to inform feature prioritization and contingency planning.

---

## 11. Milestones & Success Criteria

| Milestone | Target Date | Success Criteria | Funding Impact |
|-----------|------------|------------------|----------------|
| **MVP Launch** | [Date] | [N] early adopters, [%] satisfaction | Validates concept |
| **Product-Market Fit** | [Date] | [N] paying customers, < [%] churn | Raises seed round |
| **Break-Even** | [Date] | MRR > monthly costs | Self-sustaining |
| **Series A Readiness** | [Date] | $[Amount] ARR, [X]% growth | Scales business |

---

**Citations:**
{self._format_citations(citations)}

---
**Document Version:** 1.0
**Last Updated:** [Date]
**Status:** Ready for Investor Review
"""
        
        model_result = self.llm.generate_with_grounding(model_prompt, model_name=self.model_name)
        financial_model = model_result["text"]
        
        add_status_message(state, "Financial Modeler: Financial model complete.")
        
        return financial_model
    
    def _format_citations(self, citations: list) -> str:
        """Format citations for markdown"""
        if not citations:
            return "No citations available."
        
        formatted = "\n**Financial Data Sources:**\n"
        for i, c in enumerate(citations, 1):
            formatted += f"{i}. [{c.get('title', 'Source')}]({c.get('uri', '#')})\n"
        return formatted
