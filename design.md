# Design Document: Gram Vaani

## System Goals

Transform rural Indian agriculture through voice-first AI that combines community intelligence, weather data, and expert validation to deliver trusted, hyperlocal agricultural guidance accessible via basic phones.

**Core Objectives:**
- Voice-first accessibility for 5 Indian languages with dialect awareness
- Community-verified intelligence preventing generic AI hallucinations
- 99.5% uptime, <15s end-to-end latency on 2G networks
- Serverless AWS architecture for cost-efficiency and national scale
- Privacy-first design with 7-day voice retention, encrypted data
- Evolution path: Reactive assistant → Predictive intelligence → National digital infrastructure

## High-Level Architecture

```
Farmer (Basic Phone) → Amazon Connect/Lex → Transcribe/Polly
                                ↓
                    Lambda Orchestration Layer
                                ↓
        ┌───────────┬───────────┬───────────┬───────────┐
        ↓           ↓           ↓           ↓           ↓
   Community    AI Reasoning  Trust Layer  Feedback   Expert
   Intelligence  (Bedrock)    (Scoring)    Loop       Queue
        ↓           ↓           ↓           ↓           ↓
                    DynamoDB + S3 + SNS
                                ↓
                    Weather APIs + Govt Feeds
```

**Architecture Principles:**
- Serverless-first: Lambda compute, DynamoDB state, S3 storage
- Event-driven: SNS async processing, DynamoDB Streams triggers
- Regional: ap-south-1 (Mumbai) for latency optimization
- Stateless: Horizontal scaling, fault tolerance

## Voice Pipeline

### Input Processing
Farmer call → Lex language detection → Transcribe with 5000+ agricultural term vocabulary → Intent classification → Query routing

**Bharat Optimization:**
- 8kHz sampling for basic phone compatibility
- Adaptive bitrate (16-64kbps) based on network quality
- Noise reduction for rural environments (SNR <10dB)
- Dialect-specific phonetic mappings per language

### Output Delivery
Advisory text → SSML formatting (pauses, emphasis) → Polly neural voices (Aditi/Hindi, Kajal/Marathi) → Streaming audio delivery

**Trust-Centric Voice Design:**
- Reassuring tone for low-confidence advisories (slower pace, softer emphasis)
- Confident tone for validated advice (normal pace, clear emphasis)
- Culturally contextual phrasing (reference local festivals for timing, village-familiar crop names)
- Village-referenced explanations ("Farmers in Shirur village reported success")

**Low-Connectivity Resilience:**
- Progressive audio delivery (resume on disconnect)
- 16kbps compression for 2G networks
- Phrase caching in S3 (24h TTL) to reduce Polly costs
- SMS fallback for dropped calls

## AI Reasoning Layer

### Prompt Architecture
```
Context: {district}, {crop}, {growth_stage}, {query}
Community Intelligence: {top_3_district_reports}, {village_trust_scores}
Weather: {current_conditions}, {3_day_forecast}
Government: {relevant_state_advisories}

Task: Provide actionable advice with:
1. Direct answer
2. Community evidence reasoning
3. Specific actions + timeline
4. Confidence level + justification
```

**Model:** Amazon Bedrock (Claude 3 Haiku for cost-efficiency)

**AI Differentiation:**
- Dialect-aware intent understanding (5000+ agricultural terms, regional phonetic mappings)
- Community pattern learning (semantic clustering of farmer reports via embeddings)
- Behavioral adaptation (learn which advice types drive adoption per farmer segment)
- Risk prediction using spatial clustering + temporal correlation + weather signals

**Fallback Strategy:**
- Bedrock timeout (>3s) → cached similar query
- Low confidence (<0.4) → escalate to expert queue
- No community data → weather + govt feeds only (confidence -0.3)

### Response Structure
Extract JSON: `{advice, reasoning, actions[], confidence}` → Validate against Trust Layer → Convert to natural language → Voice synthesis

## Community Intelligence Engine

### Report Lifecycle
Voice report → Transcribe → Spam detection → DynamoDB (90d TTL) + S3 (7d) → Hourly clustering (Bedrock embeddings) → Consensus detection (≥3 similar reports) → Trust score weighting

**Validation:**
- Duplicate detection (same phone, 1h window)
- Cross-village validation (flag if contradicts 80% of reports)
- Reporter credibility scoring (0.0-1.0 based on feedback history)

### Village Trust Index
```
Trust_Score = 0.4 * feedback_accuracy + 0.3 * report_verification + 
              0.2 * community_engagement + 0.1 * historical_reliability
```

**Updates:**
- Positive feedback: +0.05 (max 1.0)
- Negative feedback: -0.1 (min 0.0)
- Temporal decay: -0.02/week if no reports (toward 0.5 baseline)
- Weekly recalculation via batch Lambda

## Trust & Confidence Scoring

### Confidence Formula
```
Confidence = min(1.0,
  0.35 * community_agreement +
  0.25 * weather_data_quality +
  0.20 * village_trust_index +
  0.15 * ai_model_confidence +
  0.05 * govt_advisory_alignment
)
```

**Communication:**
- High (≥0.7): "Highly confident based on {N} farmer reports"
- Medium (0.5-0.7): "Verify with local conditions"
- Low (<0.5): "Limited information. Consult agricultural officer"

### Explainability
Every advisory includes:
1. Community evidence: "8 farmers in Shirur village reported success"
2. Weather context: "No rain for 3 days, spray will be effective"
3. Expert validation: "Verified by Dr. Patil, Pune district officer"
4. Confidence reasoning: "High confidence (0.82) from strong agreement"

## Predictive Intelligence Layer

### Outbreak Detection Pipeline
```
Community Reports → Symptom Clustering (Bedrock embeddings, 6h batch)
                 → Spatial Analysis (DBSCAN, ε=50km, minPts=3)
                 → Temporal Correlation (3-year historical lookback)
                 → Risk Scoring (cluster density + weather + crop stage)
                 → Proactive Alerts (risk >0.7)
```

**Early Warning Capabilities:**
- Detect emerging patterns (≥5 similar reports in district within 7 days)
- Pest migration tracking across districts
- Weather-risk correlation (rainfall → pest emergence 3-5 days)
- Cross-state intelligence sharing for national-scale alerts

**Storage:**
- outbreak_patterns_table: Historical signatures (location, crop, season, weather)
- risk_scores_table: District-crop risk scores (updated 6h)

## Human + AI Hybrid Architecture

### Expert Escalation Workflow
```
Low Confidence (<0.5) → Expert Queue → District Officer Assignment
                     → Expert Review/Correction → Farmer Callback (2h SLA)
                     → Learning Loop Update
```

**Validation Queues:**
- High-Stakes: Pesticide recommendations, disease diagnosis (always require expert)
- Low-Confidence: <0.5 advisories (2h expert review)
- Anomaly: Contradicts govt guidelines or weather (immediate review)
- Learning: Random 5% sample for quality assurance

**RLHF Integration:**
- Expert corrections → prompt engineering updates (weekly)
- Farmer outcomes + expert validations → reward model
- Monthly policy updates based on accumulated feedback
- A/B testing prompt variations (10% traffic)

## Trust Graph Architecture

### Graph Structure
**Nodes:** Villages (600k+), Reporters (farmers), Experts (officers)
**Edges:** Report citations, Feedback links, Validation links
**Weights:** Trust scores, feedback sentiment, validation outcomes

**Storage:** DynamoDB adjacency list with village_id → connected_villages + trust_scores

### Credibility Propagation
- Reporter credibility: 0.0-1.0 based on verified report history
- Village credibility: Aggregate of reporter scores
- Cross-validation boost: +0.1 if validated by ≥2 neighboring villages
- Temporal decay: -0.02/week toward 0.5 baseline

### Report Weighting
```
Weight = reporter_credibility * village_trust * recency_factor * cross_validation_multiplier
Where: recency = 1.0 (<24h), 0.8 (<7d), 0.5 (<30d)
       cross_validation = 1.5 (≥2 villages), 1.0 (default)
```

## Geo-Spatial Intelligence Layer

### Spatial Clustering
DBSCAN on report coordinates (ε=50km, minPts=3) → Identify outbreak hotspots → Geohash indexing for proximity queries → 6h batch processing

### District Trend Mapping
Daily rollup: district → issue_type → count → Compare to 4-week baseline → Flag >50% increases → Generate heatmaps for agricultural departments

### Risk Heatmaps
Taluk-level risk scores (6h updates) combining spatial clusters + weather forecasts + historical data → Color coding: Green (<0.3), Yellow (0.3-0.6), Orange (0.6-0.8), Red (>0.8)

### Hyperlocal Advisory Generation
- Prioritize reports from <20km radius
- Reference specific villages, taluks, landmarks
- Adapt for microclimate (elevation, soil, irrigation metadata)

## Adoption Infrastructure Layer

### Onboarding Channels
**Krishi Kendras:** 2h staff training → Demo scripts → Farmer phone entry → System-initiated tutorial call
**NGO/FPO:** Village awareness campaigns → Performance-based incentives (farmers with ≥3 calls in first month)
**Fertilizer Shops:** Point-of-sale toll-free number distribution → Unique referral codes → Discount for first-time callers

### First-Call Experience
60s tutorial in farmer's language → Interactive demo (sample question) → Callback scheduling (opt-in, 2-day follow-up)

### Trust-Building Strategy
- Gradual engagement: Weather query → Crop advice → Community report contribution
- Success stories from nearby villages
- Expert validation messaging for credibility

### Referral Tracking
DynamoDB table: farmer_phone → referral_source + code + onboarding_date + call_count + retention_status
Analytics: Channel effectiveness, geographic penetration, underserved area identification

## Data Architecture

### DynamoDB Tables
- **farmers_table**: PK=phone_number, GSI=district-index
- **community_reports_table**: PK=report_id, SK=timestamp, GSI=district-crop-timestamp, TTL=90d
- **advisories_table**: PK=advisory_id, GSI=farmer_phone-timestamp
- **village_trust_index_table**: PK=village_id
- **expert_queue_table**: PK=queue_id, SK=timestamp
- **outbreak_patterns_table**: Historical signatures
- **risk_scores_table**: District-crop risk scores
- **trust_graph_table**: Adjacency list representation

### S3 Buckets
- **voice-recordings**: 7d lifecycle, SSE-S3 encryption
- **community-reports**: 90d → Glacier
- **cached-advisories**: 24h TTL

### Event Architecture
**SNS Topics:** advisory-generated, feedback-received, system-alerts
**DynamoDB Streams:** community_reports (→ aggregator), village_trust_index (→ notifier)

## Bharat Deployment Architecture

### District Rollout Model
**Phase 1 (3mo):** 2 districts (Maharashtra, Karnataka) → 1k farmers/district → Validate voice + community intelligence
**Phase 2 (6mo):** 10 districts, 3 states → 5k farmers/district → Scale infrastructure, optimize costs
**Phase 3 (12mo):** 50 districts, 10 states → 10k farmers/district → Cross-state intelligence, predictive capabilities
**Phase 4 (24mo):** 600+ districts nationwide → 100M+ farmers → National digital infrastructure

### Rural Infrastructure Adaptation
**Network:** 2G optimization (16kbps audio, progressive delivery, 5s timeouts, 3 retries)
**Caching:** District-level edge caching via CloudFront + S3
**Latency:** <15s end-to-end on 2G networks

### AWS Regional Strategy
**Primary:** ap-south-1 (Mumbai) for lowest latency, full service availability
**Data Residency:** All farmer data in India, no cross-border transfer
**Cost:** Compute Savings Plans for Lambda (20% savings), serverless-first (no idle costs)

### State Customization
- Dialect-specific Transcribe vocabularies
- State agricultural department crop calendars, pest databases
- State-level expert network integration

## Bharat-Scale Defensibility

### Why Centralized AI Cannot Replicate This
**Network Effects:** Each farmer report increases accuracy for all farmers in that geography
**Data Density:** Village-level granularity (600k+ villages) creates hyperlocal intelligence impossible to replicate centrally
**Trust Graph:** Multi-year relationship data between villages, reporters, outcomes builds irreplaceable credibility
**Dialect Nuance:** Agricultural vocabulary varies by district; requires ground-truth data from actual farmer speech
**Behavioral Learning:** Adoption patterns only emerge from real usage feedback loops

### Long-Term Moat Strategy
- 5+ years of feedback creates defensible credibility scoring
- Farmer-reported symptoms + outcomes build proprietary disease identification dataset
- Communication style, timing, phrasing optimization per farmer segment
- 10k+ agricultural officer relationships become institutional knowledge

## National Evolution Path

### Phase 1: Voice Assistant (Current)
Reactive Q&A system → Community reports + weather + AI reasoning → District-level, 10k farmers/district → Accessible advice for low-literacy farmers

### Phase 2: Intelligence Network (12-18mo)
Proactive alerts → Outbreak detection, spatial clustering, cross-district trends → State-level, 100k farmers/state → Early warning preventing crop losses

### Phase 3: Predictive System (24-36mo)
Risk prediction → Weather-pest correlation, seasonal forecasting, behavioral learning → Multi-state, 10M farmers → Preventive guidance

### Phase 4: Agricultural Digital Infrastructure (36+mo)
National intelligence platform → Policy insights, market linkages, supply chain optimization, climate adaptation → National, 100M+ farmers → Digital public good transforming Indian agriculture

### Evolution Metrics
**Phase 1→2:** Outbreak detection >80% accuracy, proactive alert adoption >50%
**Phase 2→3:** Risk prediction >70% accuracy (7d forecast), preventive advisory adoption >60%
**Phase 3→4:** National coverage >50% districts, government integration (3+ states), market linkage operational

## Security & Privacy

**Encryption:** TLS 1.3 in transit, SSE-S3 at rest
**Access Control:** IAM least privilege, VPC private subnets, Secrets Manager (90d rotation)
**Privacy:** Anonymize reports before aggregation, 7d voice retention, farmer data deletion on request
**Compliance:** Indian data protection regulations, all data in ap-south-1
**Audit:** CloudTrail API logs, CloudWatch application logs (30d retention)

## Reliability & Scalability

**High Availability:** Multi-AZ deployment (3 AZs in ap-south-1)
**Scaling:** Lambda auto-scales to 1000 concurrent executions, DynamoDB on-demand auto-scaling
**Performance Targets:** <10s voice-to-advisory (p95), <5s advisory-to-voice (p95), <15s end-to-end on 2G (p95)
**Failure Handling:** Exponential backoff, cached fallbacks, graceful degradation, expert escalation

## MVP Architecture

**Scope (3mo):** Hindi + Marathi, 2 districts (Maharashtra), 100 concurrent calls
**Features:** Voice input/output, advisory generation with community intelligence, confidence scoring
**Integrations:** Weather API only (no govt feeds initially)
**Community Intelligence:** Lightweight implementation with manual report clustering, baseline trust scoring (0.5), validates core differentiator early
**Expert Review:** Manual validation of low-confidence advisories (<0.5)

**Evolution:** Phase 2 (automated clustering, 3 languages) → Phase 3 (automated trust updates, 10 districts) → Phase 4 (govt feeds, 1000 concurrent) → Phase 5 (full automation, nationwide)
