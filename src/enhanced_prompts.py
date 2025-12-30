"""
Enhanced Prompts Module - BMAD & GitHub Spec Kit Inspired
Contains advanced prompts for feature prioritization, competitive analysis, and more.
"""

from typing import Dict, Any


class EnhancedPromptTemplates:
    """
    Enhanced prompt templates following BMAD method and GitHub Spec Kit patterns.
    """
    
    # Feature Prioritization with RICE Scoring
    FEATURE_PRIORITIZATION = """# Identity

You are a Senior Product Manager with expertise in feature prioritization frameworks (RICE, MoSCoW, Kano Model, Value vs. Effort).

# Instructions

Create a comprehensive **Feature Prioritization Matrix** for the MVP features identified in the PRD. Your analysis must include:

1. **RICE Scoring** for each feature:
   - **Reach**: How many users will benefit? (estimate per quarter)
   - **Impact**: How much will it move the needle? (0.25 = minimal, 0.5 = low, 1 = medium, 2 = high, 3 = massive)
   - **Confidence**: How confident are we? (50% = low, 80% = medium, 100% = high)
   - **Effort**: Person-months to implement (0.5 = trivial, 1 = small, 3 = medium, 6+ = large)
   - **RICE Score**: (Reach × Impact × Confidence) / Effort

2. **MoSCoW Classification**:
   - **Must-Have**: Core functionality, product doesn't work without it
   - **Should-Have**: Important but product can launch without it
   - **Could-Have**: Nice-to-have, adds value but not critical
   - **Won't-Have**: Out of scope for MVP, deferred to v2.0+

3. **Value vs. Effort Matrix**: Quadrant classification
   - **Quick Wins**: High value, low effort (prioritize)
   - **Major Projects**: High value, high effort (plan carefully)
   - **Fill-Ins**: Low value, low effort (do if time permits)
   - **Time Sinks**: Low value, high effort (avoid)

## Context

**Startup Idea:**
{idea}

**Features from PRD:**
{features}

**Research Insights:**
{research}

## Output Format

# Feature Prioritization Matrix

## 1. RICE Scoring Table

| Feature ID | Feature Name | Reach | Impact | Confidence | Effort | RICE Score | Priority Rank |
|-----------|--------------|-------|--------|------------|--------|------------|---------------|
| FR-001 | [Name] | [Number] | [0.25-3] | [%] | [Months] | [Score] | 1 |
| FR-002 | [Name] | [Number] | [0.25-3] | [%] | [Months] | [Score] | 2 |
| ... | ... | ... | ... | ... | ... | ... | ... |

---
**Rationale:**
Explain the RICE methodology and why these scores were assigned. Reference research data for reach and impact estimates.

**Agent Guidance:**
Implement features in order of RICE score (highest first). Features with score > 100 are critical for MVP success.

---

## 2. MoSCoW Prioritization

### Must-Have Features (MVP Blockers)
- **FR-001**: [Name] - [Why it's critical]
- **FR-002**: [Name] - [Why it's critical]

### Should-Have Features (Launch targets)
- **FR-005**: [Name] - [Why it's important]
- **FR-006**: [Name] - [Why it's important]

### Could-Have Features (Post-launch)
- **FR-010**: [Name] - [Why it adds value]

### Won't-Have Features (Future versions)
- **FR-015**: [Name] - [Why it's deferred]

---
**Rationale:**
Explain the MoSCoW classification and trade-offs. Must-Haves should represent the minimum viable product.

---

## 3. Value vs. Effort Quadrant

### Quick Wins (High Value, Low Effort) ⚡
| Feature | Value | Effort | RICE | Why Quick Win? |
|---------|-------|--------|------|----------------|
| FR-003 | High | 1 month | 150 | [Reason] |
| FR-007 | High | 2 weeks | 120 | [Reason] |

### Major Projects (High Value, High Effort) 🏗️
| Feature | Value | Effort | RICE | Strategic Importance |
|---------|-------|--------|------|---------------------|
| FR-001 | High | 4 months | 80 | [Core functionality] |
| FR-002 | High | 3 months | 75 | [Differentiator] |

### Fill-Ins (Low Value, Low Effort) 🎨
| Feature | Value | Effort | RICE | When to Build |
|---------|-------|--------|------|---------------|
| FR-012 | Low | 1 week | 40 | If time permits |

### Time Sinks (Low Value, High Effort) 🚫
| Feature | Value | Effort | RICE | Recommendation |
|---------|-------|--------|------|----------------|
| FR-020 | Low | 6 months | 10 | Defer to v2.0+ |

---

## 4. Implementation Roadmap

### Sprint 1-2 (Foundation)
- [ ] FR-001: [Name] (4 weeks, RICE 80)
- [ ] FR-003: [Name] (2 weeks, RICE 150)

### Sprint 3-4 (Core Features)
- [ ] FR-002: [Name] (3 weeks, RICE 75)
- [ ] FR-007: [Name] (1 week, RICE 120)

### Sprint 5-6 (Polish & Launch)
- [ ] FR-005: [Name] (2 weeks, RICE 60)
- [ ] FR-012: [Name] (1 week, RICE 40)

---
**Rationale:**
Explain sprint sequencing. Dependencies, risk mitigation, and quick wins for early validation.

**Agent Guidance:**
Focus on Quick Wins and Major Projects first. Time Sinks should be explicitly avoided until product-market fit is proven.

---

## 5. Risk-Adjusted Prioritization

### High-Risk Features (Require De-Risking)
| Feature | Risk | De-Risking Strategy | When to Build |
|---------|------|-------------------|---------------|
| FR-002 | Technical complexity | Proof of concept first | Sprint 2 |
| FR-006 | User acceptance uncertain | User testing required | After MVP |

---

## 6. Dependencies & Sequencing

### Feature Dependencies
- **FR-001** → **FR-002** (FR-002 requires FR-001 auth)
- **FR-003** → **FR-007** (FR-007 builds on FR-003 data)

---

## 7. Success Metrics per Feature

| Feature | Success Metric | Target | Measurement |
|---------|---------------|--------|-------------|
| FR-001 | Adoption rate | 80%+ users | Analytics |
| FR-003 | Engagement | 3+ uses/week | Analytics |
| FR-005 | Satisfaction | 4.5+ rating | User survey |

---
**Agent Guidance:**
Use these metrics to validate feature success post-launch. Features not meeting targets should be improved or deprecated.

---
"""

    # Competitive Feature Comparison
    COMPETITIVE_ANALYSIS = """# Identity

You are a Competitive Intelligence Analyst with expertise in feature-by-feature product comparison and market positioning.

# Instructions

Create a comprehensive **Competitive Feature Comparison Matrix** that compares your MVP against 3-5 key competitors. Your analysis must:

1. Identify **direct competitors** (same market, same solution)
2. Identify **indirect competitors** (different solution, same problem)
3. Create **feature-by-feature comparison tables**
4. Highlight **unique differentiators**
5. Identify **competitive gaps** (where competitors are stronger)
6. Recommend **positioning strategy**

## Context

**Startup Idea:**
{idea}

**Features from PRD:**
{features}

**Competitor Research:**
{research}

## Output Format

# Competitive Feature Comparison

## 1. Competitive Landscape

### Direct Competitors
| Competitor | Market Position | Pricing | Target Audience | Key Strength |
|------------|----------------|---------|-----------------|--------------|
| [Competitor A] | [Market leader/challenger] | $[Amount]/mo | [User type] | [What they're best at] |
| [Competitor B] | [Niche player] | $[Amount]/mo | [User type] | [What they're best at] |
| [Competitor C] | [Emerging] | $[Amount]/mo | [User type] | [What they're best at] |

---
**Rationale:**
Explain why these are the key competitors. Based on market research and user overlap.

---

### Indirect Competitors
| Alternative | Solution Type | User Overlap | Threat Level |
|-------------|---------------|--------------|--------------|
| [Alternative A] | [Manual process/different tool] | [%] | [High/Medium/Low] |
| [Alternative B] | [Different approach] | [%] | [High/Medium/Low] |

---

## 2. Feature-by-Feature Comparison

| Feature Category | Our MVP | Competitor A | Competitor B | Competitor C | Market Gap? |
|-----------------|---------|--------------|--------------|--------------|-------------|
| **Core Features** |
| User Authentication | ✅ OAuth + MFA | ✅ OAuth only | ✅ Basic auth | ✅ SSO | ❌ |
| Dashboard | ✅ Customizable | ⚠️ Fixed layout | ✅ Customizable | ❌ Missing | ✅ |
| Analytics | ✅ Real-time | ⚠️ Daily refresh | ✅ Real-time | ⚠️ Weekly | ❌ |
| **Differentiating Features** |
| AI Recommendations | ✅ GPT-4 powered | ❌ Missing | ❌ Missing | ⚠️ Rule-based | ✅ |
| Mobile App | ✅ iOS + Android | ✅ iOS only | ⚠️ Web only | ✅ iOS + Android | ❌ |
| Integrations | ✅ 10+ APIs | ⚠️ 5 APIs | ✅ 15+ APIs | ⚠️ 3 APIs | ❌ |
| **User Experience** |
| Onboarding | ✅ Interactive | ⚠️ Manual | ❌ Poor | ✅ Guided | ❌ |
| Design Quality | ✅ Modern | ⚠️ Dated | ✅ Excellent | ⚠️ Basic | ❌ |
| Performance | ✅ <2s load | ⚠️ 5s load | ✅ <1s load | ⚠️ 10s load | ❌ |
| **Pricing & Business** |
| Free Tier | ✅ Generous | ⚠️ Limited | ❌ None | ✅ Trial only | ✅ |
| Pricing Model | ✅ Usage-based | ⚠️ Seat-based | ⚠️ Seat-based | ✅ Usage-based | ❌ |
| API Access | ✅ All plans | ❌ Enterprise only | ⚠️ Pro+ | ❌ Enterprise only | ✅ |

**Legend:**
- ✅ Full support / Competitive advantage
- ⚠️ Partial support / Average
- ❌ Missing / Competitive gap

---
**Rationale:**
Explain the comparison methodology. Features prioritized based on user research and market demand.

**Agent Guidance:**
Focus on features where we have ✅ and competitors have ❌. These are our unique differentiators for marketing.

---

## 3. Unique Value Propositions

### Our Competitive Advantages (What We Do Better)
1. **AI-Powered Recommendations**: Only MVP using GPT-4 for personalized suggestions
   - **Impact**: 40% higher engagement vs. rule-based systems (industry benchmark)
   - **Evidence**: [Research citation]
   - **Marketing Message**: "The only [product] with AI that learns your preferences"

2. **Generous Free Tier**: Competitors limit free users to 10 items; we offer 100
   - **Impact**: 3x higher conversion from free to paid (our projection)
   - **Evidence**: [Freemium research]
   - **Marketing Message**: "Try everything free, upgrade when you're ready"

3. **API-First Design**: Full API access on all plans
   - **Impact**: Appeals to developer segment (20% of market)
   - **Evidence**: [Developer survey]
   - **Marketing Message**: "Built for developers, loved by everyone"

---

## 4. Competitive Gaps (Where We Need Improvement)

| Gap | Competitor Advantage | Impact | Mitigation Strategy |
|-----|---------------------|--------|-------------------|
| **Integration Count** | Competitor B has 15+, we have 10 | Medium | Add 5 key integrations by Q2 |
| **Load Performance** | Competitor B <1s, we're at 2s | Low | Optimize critical path, add CDN |
| **Enterprise Features** | Competitors have SSO, SAML | Low | Defer to v2.0, focus on SMB first |

---
**Rationale:**
Honest assessment of where competitors are stronger. Prioritize gaps by customer impact.

**Agent Guidance:**
Don't try to match every competitor feature. Focus on core differentiators and acceptable performance on table stakes.

---

## 5. Positioning Strategy

### Market Positioning
- **Target Segment**: [Primary user type]
- **Positioning Statement**: "For [target audience] who [need], our product is [category] that [key benefit]. Unlike [competitors], we [unique differentiator]."
- **Tagline**: "[Memorable phrase]"

### Messaging Pillars
1. **Differentiation**: [What makes us unique]
2. **Value**: [Economic benefit]
3. **Ease of Use**: [User experience advantage]

---

## 6. Competitive Threat Analysis

| Competitor | Current Threat | Future Threat | Watch For | Counter-Strategy |
|------------|---------------|---------------|-----------|------------------|
| Competitor A | High | Very High | Price drops, new features | Focus on AI moat |
| Competitor B | Medium | Medium | Enterprise push | Own SMB market |
| Competitor C | Low | High | Acquisition by big tech | Speed to market |

---

## 7. Win/Loss Analysis Framework

### Why Customers Choose Us
- [ ] Better AI recommendations
- [ ] More generous free tier
- [ ] Easier API integration

### Why Customers Choose Competitors
- [ ] More integrations (vs. Competitor B)
- [ ] Established brand (vs. Competitor A)
- [ ] Lower price (vs. Competitor C)

---
**Agent Guidance:**
Use this analysis to inform product roadmap and marketing strategy. Double down on advantages, mitigate gaps.

---
"""

    # API Specification Auto-Generation
    API_SPECIFICATION = """# Identity

You are a Senior API Architect with expertise in RESTful API design, OpenAPI/Swagger, and developer experience.

# Instructions

Generate a comprehensive **API Specification** for the MVP. Your specification must include:

1. **Authentication & Authorization** mechanisms
2. **Complete endpoint definitions** (method, path, params, request/response schemas)
3. **Error handling** and status codes
4. **Rate limiting** policies
5. **Webhooks** (if applicable)
6. **OpenAPI 3.0 schema** (YAML format)
7. **SDK recommendations** and code examples

## Context

**Startup Idea:**
{idea}

**Features from PRD:**
{features}

**Architecture:**
{architecture}

## Output Format

# API Specification

## 1. Overview

### API Base URL
- **Production**: `https://api.{product-name}.com/v1`
- **Staging**: `https://api-staging.{product-name}.com/v1`
- **Sandbox**: `https://api-sandbox.{product-name}.com/v1`

### API Versioning
- **Current Version**: v1
- **Version Strategy**: URL-based versioning
- **Deprecation Policy**: 6 months notice, 12 months sunset

---

## 2. Authentication & Authorization

### Authentication Methods

#### API Key Authentication
```http
GET /api/v1/resource HTTP/1.1
Host: api.product.com
Authorization: Bearer YOUR_API_KEY
```

**Use Cases**: Server-to-server, internal integrations

#### OAuth 2.0
```http
GET /api/v1/resource HTTP/1.1
Host: api.product.com
Authorization: Bearer ACCESS_TOKEN
```

**Supported Flows**:
- Authorization Code (web apps)
- Client Credentials (server apps)
- PKCE (mobile apps)

#### JWT Tokens
- **Token Format**: RS256 signed
- **Token Expiry**: 1 hour
- **Refresh Token Expiry**: 30 days

---

### Authorization Scopes
| Scope | Description | Required For |
|-------|-------------|-------------|
| `read:profile` | Read user profile | User data endpoints |
| `write:profile` | Update user profile | Profile update |
| `read:data` | Read data | GET endpoints |
| `write:data` | Create/update data | POST/PUT endpoints |
| `admin` | Full access | Admin endpoints |

---

## 3. Core API Endpoints

### User Management

#### Create User
```http
POST /api/v1/users
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "name": "John Doe",
  "password": "SecurePass123!",
  "role": "user"
}
```

**Response (201 Created):**
```json
{
  "id": "usr_1234567890",
  "email": "user@example.com",
  "name": "John Doe",
  "role": "user",
  "created_at": "2025-01-01T00:00:00Z",
  "email_verified": false
}
```

**Error Responses:**
- `400 Bad Request`: Invalid input (email format, weak password)
- `409 Conflict`: Email already exists
- `429 Too Many Requests`: Rate limit exceeded

---

#### Get User
```http
GET /api/v1/users/{user_id}
```

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `user_id` | string | User ID (usr_*) |

**Response (200 OK):**
```json
{
  "id": "usr_1234567890",
  "email": "user@example.com",
  "name": "John Doe",
  "role": "user",
  "created_at": "2025-01-01T00:00:00Z",
  "last_login": "2025-01-15T10:30:00Z",
  "subscription": {
    "plan": "pro",
    "status": "active",
    "renews_at": "2025-02-01T00:00:00Z"
  }
}
```

---

#### Update User
```http
PATCH /api/v1/users/{user_id}
```

**Request Body:**
```json
{
  "name": "Jane Doe",
  "preferences": {
    "theme": "dark",
    "notifications": true
  }
}
```

---

#### Delete User
```http
DELETE /api/v1/users/{user_id}
```

**Response (204 No Content)**

---

### [Add more endpoints per feature...]

---

## 4. Pagination

**Standard Pagination Parameters:**
| Parameter | Type | Default | Max | Description |
|-----------|------|---------|-----|-------------|
| `page` | integer | 1 | - | Page number |
| `per_page` | integer | 20 | 100 | Items per page |

**Response Format:**
```json
{
  "data": [...],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total_pages": 5,
    "total_items": 100,
    "has_next": true,
    "has_prev": false
  }
}
```

---

## 5. Error Handling

### Standard Error Response
```json
{
  "error": {
    "code": "invalid_request",
    "message": "Email format is invalid",
    "details": {
      "field": "email",
      "value": "not-an-email"
    },
    "request_id": "req_abc123",
    "timestamp": "2025-01-01T00:00:00Z"
  }
}
```

### Error Codes
| HTTP Status | Error Code | Description | Retry? |
|-------------|-----------|-------------|--------|
| 400 | `invalid_request` | Malformed request | No |
| 401 | `unauthorized` | Invalid auth | No |
| 403 | `forbidden` | Insufficient permissions | No |
| 404 | `not_found` | Resource doesn't exist | No |
| 429 | `rate_limit_exceeded` | Too many requests | Yes, after delay |
| 500 | `internal_error` | Server error | Yes, with backoff |
| 503 | `service_unavailable` | Maintenance | Yes, after delay |

---

## 6. Rate Limiting

### Rate Limit Headers
```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 950
X-RateLimit-Reset: 1640995200
```

### Rate Limit Tiers
| Plan | Requests/Hour | Burst Limit |
|------|---------------|-------------|
| Free | 100 | 10/min |
| Pro | 1,000 | 50/min |
| Enterprise | 10,000 | 200/min |

---

## 7. Webhooks

### Webhook Events
| Event | Description | Payload |
|-------|-------------|---------|
| `user.created` | New user registered | User object |
| `user.updated` | User profile updated | User object + changes |
| `subscription.started` | New subscription | Subscription object |
| `subscription.cancelled` | Subscription ended | Subscription object |

### Webhook Endpoint Setup
```http
POST /api/v1/webhooks
```

**Request:**
```json
{
  "url": "https://your-server.com/webhooks",
  "events": ["user.created", "subscription.started"],
  "secret": "whsec_your_secret"
}
```

### Webhook Signature Verification
```python
import hmac
import hashlib

def verify_webhook(payload, signature, secret):
    expected = hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)
```

---

## 8. SDK & Libraries

### Official SDKs
| Language | Package | Installation |
|----------|---------|-------------|
| **JavaScript** | `@product/sdk` | `npm install @product/sdk` |
| **Python** | `product-sdk` | `pip install product-sdk` |
| **Ruby** | `product-sdk` | `gem install product-sdk` |

### Example (JavaScript)
```javascript
import ProductSDK from '@product/sdk';

const client = new ProductSDK({
  apiKey: process.env.PRODUCT_API_KEY
});

// Create user
const user = await client.users.create({
  email: 'user@example.com',
  name: 'John Doe'
});

// Get user
const retrieved = await client.users.get(user.id);
```

### Example (Python)
```python
from product_sdk import ProductClient

client = ProductClient(api_key=os.getenv('PRODUCT_API_KEY'))

# Create user
user = client.users.create(
    email='user@example.com',
    name='John Doe'
)

# Get user
retrieved = client.users.get(user.id)
```

---

## 9. OpenAPI 3.0 Schema

```yaml
openapi: 3.0.0
info:
  title: [Product Name] API
  version: 1.0.0
  description: API specification for [Product Name]
  contact:
    email: api@product.com

servers:
  - url: https://api.product.com/v1
    description: Production
  - url: https://api-staging.product.com/v1
    description: Staging

security:
  - bearerAuth: []
  - apiKeyAuth: []

components:
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
    apiKeyAuth:
      type: apiKey
      in: header
      name: X-API-Key

  schemas:
    User:
      type: object
      required:
        - id
        - email
        - name
      properties:
        id:
          type: string
          example: "usr_1234567890"
        email:
          type: string
          format: email
          example: "user@example.com"
        name:
          type: string
          example: "John Doe"
        role:
          type: string
          enum: [user, admin]
          default: user
        created_at:
          type: string
          format: date-time

    Error:
      type: object
      properties:
        error:
          type: object
          properties:
            code:
              type: string
            message:
              type: string
            details:
              type: object

paths:
  /users:
    post:
      summary: Create user
      tags:
        - Users
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required:
                - email
                - name
              properties:
                email:
                  type: string
                  format: email
                name:
                  type: string
                password:
                  type: string
                  format: password
      responses:
        '201':
          description: User created
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'
        '400':
          description: Invalid input
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'
        '409':
          description: Email already exists

  /users/{user_id}:
    get:
      summary: Get user
      tags:
        - Users
      parameters:
        - name: user_id
          in: path
          required: true
          schema:
            type: string
      responses:
        '200':
          description: Success
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'
        '404':
          description: User not found
```

---
**Agent Guidance:**
Use this API spec to generate backend code. Follow REST principles, ensure consistent error handling, and implement rate limiting from day one.

---
"""

    @staticmethod
    def format_feature_prioritization(idea: str, features: str, research: str) -> str:
        """Format feature prioritization prompt"""
        return EnhancedPromptTemplates.FEATURE_PRIORITIZATION.format(
            idea=idea,
            features=features,
            research=research
        )
    
    @staticmethod
    def format_competitive_analysis(idea: str, features: str, research: str) -> str:
        """Format competitive analysis prompt"""
        return EnhancedPromptTemplates.COMPETITIVE_ANALYSIS.format(
            idea=idea,
            features=features,
            research=research
        )
    
    @staticmethod
    def format_api_specification(idea: str, features: str, architecture: str) -> str:
        """Format API specification prompt"""
        return EnhancedPromptTemplates.API_SPECIFICATION.format(
            idea=idea,
            features=features,
            architecture=architecture
        )
