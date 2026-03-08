# MongoDB Collections Schema for Smart Farm Advisor

## Collection 1: `environmental_profiles`

Stores environmental data for user locations.

```javascript
{
  _id: ObjectId,
  user_id: ObjectId,  // Reference to users collection
  location: {
    city: String,
    state: String,
    coordinates: {
      lat: Number,
      lng: Number
    }
  },
  temperature: Number,  // in Celsius
  humidity: Number,     // percentage
  rainfall: Number,     // in mm
  nitrogen: Number,     // soil nitrogen level (0-100)
  phosphorus: Number,   // soil phosphorus level (0-100)
  potassium: Number,    // soil potassium level (0-100)
  soil_ph: Number,      // pH level (0-14)
  soil_temperature: Number,  // in Celsius
  soil_humidity: Number,     // percentage
  rainfall_annual: Number,   // in mm
  last_updated: Date,
  created_at: Date
}
```

**Example Document:**
```javascript
{
  _id: ObjectId("507f1f77bcf86cd799439011"),
  user_id: ObjectId("507f1f77bcf86cd799439012"),
  location: {
    city: "Kunchanapalli",
    state: "Andhra Pradesh",
    coordinates: { lat: 14.4426, lng: 79.9865 }
  },
  temperature: 12,
  humidity: 37,
  rainfall: 100,
  nitrogen: 50,
  phosphorus: 50,
  potassium: 50,
  soil_ph: 8.5,
  soil_temperature: 12,
  soil_humidity: 37,
  rainfall_annual: 100,
  last_updated: new Date(),
  created_at: new Date()
}
```

---

## Collection 2: `crop_recommendations`

Stores crop recommendation data with suitability scores.

```javascript
{
  _id: ObjectId,
  crop_name: String,
  climate_match: String,  // "Climate Match" label
  soil_compatibility: Number,  // percentage (0-100)
  water_requirement: String,   // "High", "Moderate", "Low"
  water_level: String,         // "Water: High", "Water: Moderate"
  yield_potential: String,     // "High", "Moderate", "Low"
  optimal_conditions: {
    temperature_min: Number,
    temperature_max: Number,
    humidity_min: Number,
    humidity_max: Number,
    rainfall_min: Number,
    rainfall_max: Number,
    nitrogen_min: Number,
    nitrogen_max: Number,
    phosphorus_min: Number,
    phosphorus_max: Number,
    potassium_min: Number,
    potassium_max: Number,
    ph_min: Number,
    ph_max: Number
  },
  growing_season: String,
  market_demand: String,
  created_at: Date
}
```

**Example Documents:**
```javascript
[
  {
    _id: ObjectId("507f1f77bcf86cd799439013"),
    crop_name: "Mango",
    climate_match: "Climate Match",
    soil_compatibility: 24,
    water_requirement: "Moderate",
    water_level: "Water: Moderate",
    yield_potential: "High",
    optimal_conditions: {
      temperature_min: 24,
      temperature_max: 30,
      humidity_min: 50,
      humidity_max: 80,
      rainfall_min: 750,
      rainfall_max: 2500,
      nitrogen_min: 40,
      nitrogen_max: 60,
      phosphorus_min: 30,
      phosphorus_max: 50,
      potassium_min: 40,
      potassium_max: 60,
      ph_min: 5.5,
      ph_max: 7.5
    },
    growing_season: "Summer",
    market_demand: "High",
    created_at: new Date()
  },
  {
    _id: ObjectId("507f1f77bcf86cd799439014"),
    crop_name: "Mothbeans",
    climate_match: "Climate Match",
    soil_compatibility: 17,
    water_requirement: "Moderate",
    water_level: "Water: Moderate",
    yield_potential: "Moderate",
    optimal_conditions: {
      temperature_min: 25,
      temperature_max: 35,
      humidity_min: 40,
      humidity_max: 70,
      rainfall_min: 400,
      rainfall_max: 800,
      nitrogen_min: 30,
      nitrogen_max: 50,
      phosphorus_min: 40,
      phosphorus_max: 60,
      potassium_min: 30,
      potassium_max: 50,
      ph_min: 6.0,
      ph_max: 8.0
    },
    growing_season: "Kharif",
    market_demand: "Moderate",
    created_at: new Date()
  },
  {
    _id: ObjectId("507f1f77bcf86cd799439015"),
    crop_name: "Papaya",
    climate_match: "Climate Match",
    soil_compatibility: 15,
    water_requirement: "High",
    water_level: "Water: High",
    yield_potential: "High",
    optimal_conditions: {
      temperature_min: 22,
      temperature_max: 32,
      humidity_min: 60,
      humidity_max: 90,
      rainfall_min: 1000,
      rainfall_max: 2000,
      nitrogen_min: 50,
      nitrogen_max: 70,
      phosphorus_min: 40,
      phosphorus_max: 60,
      potassium_min: 50,
      potassium_max: 70,
      ph_min: 6.0,
      ph_max: 7.0
    },
    growing_season: "Year-round",
    market_demand: "High",
    created_at: new Date()
  }
]
```

---

## Collection 3: `optimization_strategies`

Stores farming optimization strategies with impact metrics.

```javascript
{
  _id: ObjectId,
  strategy_name: String,
  category: String,  // "Irrigation", "Fertilization", "Monitoring", "Soil Management"
  impact_level: String,  // "High", "Medium", "Low"
  difficulty: String,    // "Low", "Medium", "High"
  cost_effectiveness: String,  // "75%", "50%", etc.
  description: String,
  benefits: [String],
  implementation_steps: [String],
  suitable_for_crops: [String],
  resource_links: [String],
  badge: String,  // "Minimal", "Moderate", "High", "Peak"
  created_at: Date
}
```

**Example Documents:**
```javascript
[
  {
    _id: ObjectId("507f1f77bcf86cd799439016"),
    strategy_name: "Drip Irrigation",
    category: "Irrigation",
    impact_level: "High",
    difficulty: "Medium",
    cost_effectiveness: "75%",
    description: "Efficient water delivery system that saves 40% water",
    benefits: [
      "Reduces water consumption by 40%",
      "Improves crop yield",
      "Reduces weed growth",
      "Minimizes fertilizer loss"
    ],
    implementation_steps: [
      "Install drip lines along crop rows",
      "Connect to water source with filter",
      "Set timer for automated watering",
      "Monitor and maintain regularly"
    ],
    suitable_for_crops: ["Mango", "Papaya", "Cotton", "Vegetables"],
    resource_links: ["https://agricoop.gov.in/drip-irrigation"],
    badge: "Minimal",
    created_at: new Date()
  },
  {
    _id: ObjectId("507f1f77bcf86cd799439017"),
    strategy_name: "Precision Fertigation",
    category: "Fertilization",
    impact_level: "High",
    difficulty: "Low",
    cost_effectiveness: "75%",
    description: "Combine fertilizer with irrigation for optimal nutrient delivery",
    benefits: [
      "Reduces fertilizer waste",
      "Improves nutrient uptake",
      "Saves labor costs",
      "Increases crop quality"
    ],
    implementation_steps: [
      "Mix water-soluble fertilizers",
      "Inject into irrigation system",
      "Monitor soil nutrient levels",
      "Adjust based on crop needs"
    ],
    suitable_for_crops: ["All crops"],
    resource_links: ["https://agricoop.gov.in/fertigation"],
    badge: "Moderate",
    created_at: new Date()
  },
  {
    _id: ObjectId("507f1f77bcf86cd799439018"),
    strategy_name: "Mulching System",
    category: "Soil Management",
    impact_level: "Medium",
    difficulty: "Low",
    cost_effectiveness: "80%",
    description: "Cover soil with organic material to retain moisture and reduce weeds",
    benefits: [
      "Retains soil moisture",
      "Reduces weed growth by 70%",
      "Improves soil health",
      "Regulates soil temperature"
    ],
    implementation_steps: [
      "Spread organic mulch around plants",
      "Maintain 2-3 inch thickness",
      "Keep mulch away from plant stems",
      "Replenish as needed"
    ],
    suitable_for_crops: ["Vegetables", "Fruits", "Flowers"],
    resource_links: ["https://agricoop.gov.in/mulching"],
    badge: "Peak",
    created_at: new Date()
  },
  {
    _id: ObjectId("507f1f77bcf86cd799439019"),
    strategy_name: "Smart Monitoring",
    category: "Monitoring",
    impact_level: "High",
    difficulty: "Medium",
    cost_effectiveness: "50%",
    description: "Use sensors and IoT devices to monitor crop health in real-time",
    benefits: [
      "Early disease detection",
      "Optimized resource usage",
      "Data-driven decisions",
      "Reduced crop losses"
    ],
    implementation_steps: [
      "Install soil moisture sensors",
      "Set up weather monitoring",
      "Connect to mobile app",
      "Analyze data regularly"
    ],
    suitable_for_crops: ["All crops"],
    resource_links: ["https://agricoop.gov.in/smart-farming"],
    badge: "Peak",
    created_at: new Date()
  }
]
```

---

## Collection 4: `farm_intelligence_analytics`

Stores predictive analytics and farm intelligence data.

```javascript
{
  _id: ObjectId,
  user_id: ObjectId,
  location: String,
  load_predictions: Number,  // Number of predictions made
  top_crop: String,
  soil_stability: Number,    // percentage
  climate_risk: String,      // "Low", "Medium", "High"
  feature_importance: {
    nitrogen: Number,
    phosphorus: Number,
    potassium: Number,
    temperature: Number,
    humidity: Number,
    ph: Number,
    rainfall: Number
  },
  ai_insights: {
    soil_ph_optimal: Boolean,
    nitrogen_level: String,  // "Optimal", "Low", "High"
    rainfall_suitability: String,
    temperature_range: String
  },
  last_updated: Date,
  created_at: Date
}
```

**Example Document:**
```javascript
{
  _id: ObjectId("507f1f77bcf86cd799439020"),
  user_id: ObjectId("507f1f77bcf86cd799439012"),
  location: "Kunchanapalli",
  load_predictions: 3,
  top_crop: "mango",
  soil_stability: 86,
  climate_risk: "Low",
  feature_importance: {
    nitrogen: 20,
    phosphorus: 15,
    potassium: 15,
    temperature: 18,
    humidity: 12,
    ph: 10,
    rainfall: 10
  },
  ai_insights: {
    soil_ph_optimal: true,
    nitrogen_level: "Optimal",
    rainfall_suitability: "Suitable for mango cultivation",
    temperature_range: "Ideal for tropical crops"
  },
  last_updated: new Date(),
  created_at: new Date()
}
```

---

## Collection 5: `user_farm_profiles`

Extended user profile with farm-specific data.

```javascript
{
  _id: ObjectId,
  user_id: ObjectId,
  farm_size: Number,  // in acres
  soil_type: String,
  irrigation_type: String,
  current_crops: [String],
  farming_experience: Number,  // years
  preferred_crops: [String],
  equipment_owned: [String],
  certifications: [String],
  created_at: Date,
  updated_at: Date
}
```

---

## Indexes for Performance

```javascript
// environmental_profiles
db.environmental_profiles.createIndex({ user_id: 1 })
db.environmental_profiles.createIndex({ "location.city": 1 })
db.environmental_profiles.createIndex({ last_updated: -1 })

// crop_recommendations
db.crop_recommendations.createIndex({ crop_name: 1 })
db.crop_recommendations.createIndex({ soil_compatibility: -1 })

// optimization_strategies
db.optimization_strategies.createIndex({ category: 1 })
db.optimization_strategies.createIndex({ impact_level: 1 })

// farm_intelligence_analytics
db.farm_intelligence_analytics.createIndex({ user_id: 1 })
db.farm_intelligence_analytics.createIndex({ last_updated: -1 })
```

---

## Sample API Queries

### Get Environmental Profile
```javascript
db.environmental_profiles.findOne({ user_id: ObjectId("507f1f77bcf86cd799439012") })
```

### Get Top 3 Crop Recommendations
```javascript
db.crop_recommendations.find().sort({ soil_compatibility: -1 }).limit(3)
```

### Get Optimization Strategies by Category
```javascript
db.optimization_strategies.find({ category: "Irrigation" })
```

### Get Farm Intelligence
```javascript
db.farm_intelligence_analytics.findOne({ 
  user_id: ObjectId("507f1f77bcf86cd799439012") 
}).sort({ last_updated: -1 })
```
