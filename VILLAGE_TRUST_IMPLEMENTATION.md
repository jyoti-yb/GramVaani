# 🏘️ Village Trust Index Implementation

## Overview
Context-aware system with feedback collection to calculate village trust scores based on user satisfaction.

## Architecture

### 1. Tables Created

#### gramvaani_village_trust
```
{
  village_id: "Mumbai" (Primary Key),
  total_responses: 150,
  helpful_count: 135,
  trust_score: 90.0,  // (helpful_count / total_responses) * 100
  last_updated: "2026-03-02T..."
}
```

#### Enhanced gramvaani_user_querie
```
{
  query_id: "uuid",
  user_phone: "+919876543210",
  query: "मौसम कैसा है?",
  query_english: "What's the weather?",
  response: "आज मुंबई में...",
  language: "hi",
  timestamp: "2026-03-02T...",
  helpful: true/false/null,  // ← NEW
  feedback_text: "Very helpful"  // ← NEW
}
```

## API Endpoints

### 1. Submit Feedback
```
POST /api/feedback
{
  "query_id": "uuid",
  "helpful": true,
  "feedback_text": "Very helpful information"
}
```

### 2. Get Village Trust Score
```
GET /api/village-trust/{village_id}

Response:
{
  "village_id": "Mumbai",
  "total_responses": 150,
  "helpful_count": 135,
  "trust_score": 90.0,
  "last_updated": "2026-03-02T..."
}
```

### 3. Query with Feedback Support
```
POST /process-text
Response includes query_id:
{
  "query_id": "uuid",  // ← Use this for feedback
  "response_text": "...",
  "audio_data": "..."
}
```

## Frontend Implementation

### Add Feedback Popup (App.jsx)

```javascript
const [showFeedback, setShowFeedback] = useState(false)
const [currentQueryId, setCurrentQueryId] = useState(null)

// After receiving response
const handleResponse = (data) => {
  setCurrentQueryId(data.query_id)
  setShowFeedback(true)
  // Show response...
}

// Feedback component
<FeedbackPopup 
  queryId={currentQueryId}
  onSubmit={submitFeedback}
  onClose={() => setShowFeedback(false)}
/>

const submitFeedback = async (helpful, text) => {
  await apiClient.post('/api/feedback', {
    query_id: currentQueryId,
    helpful: helpful,
    feedback_text: text
  })
  setShowFeedback(false)
}
```

## Trust Score Calculation

**Formula:**
```
Trust Score = (Helpful Responses / Total Responses) × 100
```

**Example:**
- Total responses: 150
- Helpful: 135
- Trust Score: 90%

## Benefits

1. **Context Awareness**: System tracks user sessions and query patterns
2. **Quality Metrics**: Measures response helpfulness
3. **Village-Level Insights**: Trust scores per village/location
4. **Data for RAG**: English translations stored for training
5. **User Engagement**: Feedback loop improves system

## Setup

1. **Create tables:**
```bash
cd backend
python setup_dynamodb.py
```

2. **Restart backend:**
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

3. **Test feedback:**
```bash
curl -X POST http://localhost:8000/api/feedback \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "query_id": "uuid-here",
    "helpful": true,
    "feedback_text": "Very helpful"
  }'
```

## Village Trust Dashboard (Future)

Display trust scores by village:
- Top performing villages
- Areas needing improvement
- User satisfaction trends
- Active user counts per village

## Data Flow

```
User Query → AI Response → Return query_id
     ↓
User Feedback → Update query record
     ↓
Calculate Trust Score → Update village_trust table
     ↓
Display Trust Index → Dashboard/Analytics
```

## Metrics Tracked

1. **Response Quality**: Helpful vs Not Helpful
2. **Village Engagement**: Active users per village
3. **Trust Score**: Overall satisfaction percentage
4. **Query Patterns**: Most common questions per village
5. **Language Usage**: Preferred languages by region

---

**Status**: ✅ Backend Ready | ⏳ Frontend Feedback UI Needed
