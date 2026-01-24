"""
Industry-Specific Templates Module
Provides tailored prompts and requirements for different industries.
"""

from typing import Dict, List
from enum import Enum


class Industry(str, Enum):
    """Supported industry templates"""
    SAAS_B2B = "saas_b2b"
    SAAS_B2C = "saas_b2c"
    ECOMMERCE = "ecommerce"
    MOBILE_APP = "mobile_app"
    FINTECH = "fintech"
    HEALTHTECH = "healthtech"
    MARKETPLACE = "marketplace"
    EDTECH = "edtech"
    SOCIAL_MEDIA = "social_media"
    ENTERPRISE = "enterprise"
    GENERIC = "generic"


class IndustryTemplates:
    """Industry-specific requirements and considerations"""
    
    @staticmethod
    def get_industry_specific_requirements(industry: Industry) -> Dict[str, List[str]]:
        """Get additional requirements specific to an industry"""
        
        templates = {
            Industry.SAAS_B2B: {
                "functional_requirements": [
                    "Multi-tenant architecture with data isolation",
                    "Role-based access control (RBAC) with admin, manager, user roles",
                    "API access for integrations",
                    "SSO support (SAML, OAuth 2.0)",
                    "Team collaboration features",
                    "Usage analytics and reporting dashboard",
                    "White-label options for enterprise clients"
                ],
                "non_functional_requirements": [
                    "SOC 2 Type II compliance",
                    "GDPR compliance for EU customers",
                    "99.9% uptime SLA",
                    "Data encryption at rest and in transit",
                    "Audit logging for all actions",
                    "Role-based data access controls"
                ],
                "integrations": [
                    "Salesforce CRM integration",
                    "Slack/Microsoft Teams notifications",
                    "Zapier for automation",
                    "Webhooks for real-time events",
                    "REST API with rate limiting"
                ],
                "pricing_model": "Seat-based or usage-based SaaS pricing"
            },
            
            Industry.FINTECH: {
                "functional_requirements": [
                    "KYC/AML compliance workflow",
                    "Bank account linking (Plaid/Stripe)",
                    "Transaction history and statements",
                    "Payment processing with fraud detection",
                    "Multi-currency support",
                    "Recurring payments and subscriptions",
                    "Tax reporting and documentation"
                ],
                "non_functional_requirements": [
                    "PCI-DSS compliance for card payments",
                    "SOC 2 compliance",
                    "Two-factor authentication (2FA) mandatory",
                    "AES-256 encryption for sensitive data",
                    "Transaction monitoring and anomaly detection",
                    "99.99% uptime for payment processing"
                ],
                "regulatory": [
                    "FinCEN reporting for suspicious activity",
                    "State money transmitter licenses (if applicable)",
                    "Consumer Financial Protection Bureau (CFPB) compliance",
                    "Bank Secrecy Act (BSA) compliance"
                ],
                "security": [
                    "End-to-end encryption",
                    "Hardware security modules (HSM) for key management",
                    "Penetration testing quarterly",
                    "Bug bounty program"
                ]
            },
            
            Industry.HEALTHTECH: {
                "functional_requirements": [
                    "Patient data management",
                    "Appointment scheduling",
                    "Electronic Health Records (EHR) integration",
                    "Telemedicine video consultations",
                    "Prescription management",
                    "Lab results and imaging",
                    "Patient portal with secure messaging"
                ],
                "non_functional_requirements": [
                    "HIPAA compliance (BAA required for vendors)",
                    "Data encryption at rest (AES-256) and in transit (TLS 1.3)",
                    "Access controls with audit trails",
                    "Data retention policies (7+ years)",
                    "Disaster recovery plan (RPO < 1 hour)",
                    "PHI de-identification for analytics"
                ],
                "integrations": [
                    "EHR systems (Epic, Cerner, Allscripts)",
                    "HL7/FHIR API standards",
                    "Lab information systems (LIS)",
                    "Insurance verification APIs",
                    "E-prescribing (Surescripts)"
                ],
                "regulatory": [
                    "FDA approval if medical device",
                    "21 CFR Part 11 for electronic records",
                    "State medical board compliance"
                ]
            },
            
            Industry.ECOMMERCE: {
                "functional_requirements": [
                    "Product catalog with search and filters",
                    "Shopping cart and checkout flow",
                    "Payment gateway integration (Stripe, PayPal)",
                    "Inventory management",
                    "Order tracking and fulfillment",
                    "Customer reviews and ratings",
                    "Shipping integrations (USPS, FedEx, UPS)",
                    "Abandoned cart recovery",
                    "Discount codes and promotions"
                ],
                "non_functional_requirements": [
                    "PCI-DSS compliance for payment data",
                    "Page load time < 3 seconds",
                    "Mobile-responsive design",
                    "99.9% uptime during peak seasons",
                    "GDPR/CCPA compliance for privacy",
                    "SEO optimization for product pages"
                ],
                "integrations": [
                    "Payment gateways (Stripe, Square, PayPal)",
                    "Shipping carriers (Shippo, EasyPost)",
                    "Accounting (QuickBooks, Xero)",
                    "Email marketing (Mailchimp, Klaviyo)",
                    "Analytics (Google Analytics, Mixpanel)"
                ],
                "marketing": [
                    "Email campaigns for cart abandonment",
                    "Product recommendation engine",
                    "Referral program",
                    "Social media integration",
                    "Loyalty program"
                ]
            },
            
            Industry.MARKETPLACE: {
                "functional_requirements": [
                    "Buyer and seller user types",
                    "Product/service listing creation",
                    "Search and discovery with filters",
                    "Messaging between buyers and sellers",
                    "Payment escrow system",
                    "Rating and review system (two-way)",
                    "Dispute resolution workflow",
                    "Commission and fee management",
                    "Seller dashboard with analytics"
                ],
                "non_functional_requirements": [
                    "Trust and safety mechanisms",
                    "Fraud detection for transactions",
                    "Identity verification for sellers",
                    "Content moderation (automated + manual)",
                    "Payment security (PCI-DSS)",
                    "Scalable infrastructure for high volume"
                ],
                "marketplace_dynamics": [
                    "Chicken-and-egg problem: Acquire buyers and sellers simultaneously",
                    "Quality control for listings",
                    "Geographic expansion strategy",
                    "Liquidity (sufficient supply/demand matching)"
                ],
                "monetization": [
                    "Commission on transactions (5-20%)",
                    "Subscription for premium sellers",
                    "Advertising and promoted listings",
                    "Value-added services (insurance, verification)"
                ]
            },
            
            Industry.MOBILE_APP: {
                "functional_requirements": [
                    "Native iOS and Android apps",
                    "Push notifications",
                    "Offline mode with sync",
                    "Biometric authentication (Face ID, Touch ID)",
                    "Camera and photo integration",
                    "Location services (if applicable)",
                    "In-app purchases or subscriptions",
                    "Deep linking",
                    "App analytics and crash reporting"
                ],
                "non_functional_requirements": [
                    "App Store / Play Store guidelines compliance",
                    "App size < 100MB for initial download",
                    "Startup time < 2 seconds",
                    "Battery efficiency",
                    "Accessibility (VoiceOver, TalkBack)",
                    "Support for latest and previous 2 OS versions"
                ],
                "app_store_optimization": [
                    "App name and keywords",
                    "Screenshots and video preview",
                    "App description with features",
                    "User ratings strategy (prompt for reviews)",
                    "Regular updates (monthly releases)"
                ],
                "marketing": [
                    "Pre-launch landing page",
                    "Beta testing with TestFlight/Google Play Beta",
                    "Product Hunt launch",
                    "Influencer partnerships",
                    "App install ads (Facebook, Google)"
                ]
            },
            
            Industry.EDTECH: {
                "functional_requirements": [
                    "Course catalog and curriculum management",
                    "Video lessons with progress tracking",
                    "Quizzes and assessments",
                    "Certificates and badges",
                    "Discussion forums or community",
                    "Live classes or webinars",
                    "Assignment submission and grading",
                    "Parent/teacher dashboard",
                    "Personalized learning paths"
                ],
                "non_functional_requirements": [
                    "COPPA compliance (if targeting kids < 13)",
                    "FERPA compliance (student data privacy)",
                    "Accessibility (WCAG 2.1 AA)",
                    "Video streaming quality (adaptive bitrate)",
                    "LMS integration (Canvas, Blackboard, Moodle)",
                    "Multi-language support"
                ],
                "pedagogical_features": [
                    "Spaced repetition for retention",
                    "Gamification (points, leaderboards)",
                    "Adaptive difficulty based on performance",
                    "Peer-to-peer learning",
                    "Progress reports and analytics"
                ],
                "content": [
                    "Video production pipeline",
                    "Content licensing and copyright",
                    "Expert instructors or user-generated content",
                    "Quality control process"
                ]
            }
        }
        
        return templates.get(industry, templates[Industry.GENERIC])
    
    @staticmethod
    def get_industry_specific_prompt_additions(industry: Industry) -> str:
        """Get additional prompt context for specific industries"""
        
        prompts = {
            Industry.SAAS_B2B: """
**Industry-Specific Considerations (SaaS B2B):**
- Emphasize enterprise features: SSO, RBAC, API access, white-label
- Focus on team collaboration and admin controls
- Include SOC 2 and GDPR compliance requirements
- Pricing: Seat-based or usage-based tiers (Free trial, Pro, Enterprise)
- Sales cycle: 30-90 days, requires demos and onboarding
- Key metrics: MRR, CAC, LTV, churn rate, net revenue retention
- Integration requirements: Salesforce, Slack, Zapier, custom webhooks
""",
            
            Industry.FINTECH: """
**Industry-Specific Considerations (Fintech):**
- Regulatory compliance: PCI-DSS, KYC/AML, FinCEN, state licenses
- Security: 2FA mandatory, encryption, HSM, penetration testing
- Banking integrations: Plaid, Stripe Connect, bank APIs
- Risk management: Fraud detection, transaction monitoring
- Trust indicators: Security certifications, insurance (FDIC if applicable)
- Pricing: Transaction fees (1-3%), subscription tiers, premium features
""",
            
            Industry.HEALTHTECH: """
**Industry-Specific Considerations (Healthtech):**
- HIPAA compliance is mandatory (Business Associate Agreement)
- EHR integration: HL7, FHIR standards
- Patient consent and data privacy controls
- Telemedicine regulations vary by state
- FDA approval if diagnostic or therapeutic
- Pricing: Subscription for patients, B2B for providers
- Liability insurance and legal review required
""",
            
            Industry.ECOMMERCE: """
**Industry-Specific Considerations (E-commerce):**
- Payment security: PCI-DSS compliance, tokenization
- Shipping logistics: Carrier integrations, international shipping
- Inventory management: Real-time stock updates, low-stock alerts
- Mobile optimization: 60%+ of e-commerce is mobile
- Conversion optimization: Abandoned cart emails, one-click checkout
- Customer retention: Email marketing, loyalty programs
- Pricing: Product margins, shipping costs, returns/refunds
""",
            
            Industry.MARKETPLACE: """
**Industry-Specific Considerations (Marketplace):**
- Two-sided market dynamics: Need both buyers and sellers
- Payment escrow to protect both parties
- Trust and safety: Identity verification, ratings, disputes
- Commission model: 5-20% per transaction is typical
- Liquidity: Ensure sufficient supply/demand matching
- Geographic rollout: Start in one city/region, expand gradually
- Network effects: Value increases with more users
""",
            
            Industry.MOBILE_APP: """
**Industry-Specific Considerations (Mobile App):**
- Platform prioritization: iOS first (higher ARPU) or Android (larger market)
- App Store optimization: Keywords, screenshots, reviews
- Push notifications: Critical for engagement and retention
- Offline functionality: Sync when back online
- App size and performance: < 100MB, fast startup
- In-app purchases: Apple/Google take 15-30% cut
- Monetization: Freemium, subscription, ads, or one-time purchase
""",
            
            Industry.EDTECH: """
**Industry-Specific Considerations (EdTech):**
- Student data privacy: FERPA, COPPA compliance
- Accessibility: WCAG 2.1 AA for students with disabilities
- Pedagogical design: Learning science principles (spaced repetition, active recall)
- Content creation: Video production, expert instructors, licensing
- LMS integration: Canvas, Blackboard, Google Classroom
- Engagement: Gamification, social learning, progress tracking
- Pricing: B2C subscription or B2B institutional licensing
"""
        }
        
        return prompts.get(industry, "")
    
    @staticmethod
    def detect_industry_from_idea(idea: str) -> Industry:
        """
        Auto-detect likely industry from idea description.
        Simple keyword matching - can be enhanced with ML.
        """
        idea_lower = idea.lower()
        
        # Fintech indicators
        if any(word in idea_lower for word in ['payment', 'banking', 'finance', 'lending', 'credit', 'investing', 'cryptocurrency', 'wallet', 'transaction']):
            return Industry.FINTECH
        
        # Healthtech indicators
        if any(word in idea_lower for word in ['health', 'medical', 'patient', 'doctor', 'telemedicine', 'healthcare', 'clinical', 'hospital', 'wellness']):
            return Industry.HEALTHTECH
        
        # E-commerce indicators
        if any(word in idea_lower for word in ['e-commerce', 'ecommerce', 'online store', 'shop', 'retail', 'product catalog', 'checkout', 'shopping cart']):
            return Industry.ECOMMERCE
        
        # Marketplace indicators
        if any(word in idea_lower for word in ['marketplace', 'peer-to-peer', 'buyers and sellers', 'commission', 'listing', 'two-sided']):
            return Industry.MARKETPLACE
        
        # EdTech indicators
        if any(word in idea_lower for word in ['education', 'learning', 'course', 'student', 'teacher', 'classroom', 'edtech', 'training', 'curriculum']):
            return Industry.EDTECH
        
        # Mobile app indicators
        if any(word in idea_lower for word in ['mobile app', 'ios app', 'android app', 'push notification', 'offline mode', 'app store']):
            return Industry.MOBILE_APP
        
        # B2B SaaS indicators
        if any(word in idea_lower for word in ['saas', 'enterprise', 'b2b', 'business', 'team collaboration', 'workflow', 'productivity']):
            return Industry.SAAS_B2B
        
        # Social media indicators
        if any(word in idea_lower for word in ['social', 'community', 'social network', 'sharing', 'followers', 'feed', 'posts']):
            return Industry.SOCIAL_MEDIA
        
        return Industry.GENERIC
    
    @staticmethod
    def get_industry_name(industry: Industry) -> str:
        """Get human-readable industry name"""
        names = {
            Industry.SAAS_B2B: "SaaS (B2B)",
            Industry.SAAS_B2C: "SaaS (B2C)",
            Industry.ECOMMERCE: "E-commerce",
            Industry.MOBILE_APP: "Mobile App",
            Industry.FINTECH: "Fintech",
            Industry.HEALTHTECH: "Healthtech / Medtech",
            Industry.MARKETPLACE: "Marketplace",
            Industry.EDTECH: "EdTech",
            Industry.SOCIAL_MEDIA: "Social Media",
            Industry.ENTERPRISE: "Enterprise Software",
            Industry.GENERIC: "General / Other"
        }
        return names.get(industry, "Unknown")
