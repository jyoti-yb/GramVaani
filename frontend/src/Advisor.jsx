import React, { useState, useEffect } from 'react'
import { Cloud, Droplets, Wind, AlertTriangle, Sprout, TrendingUp, ChevronDown, ChevronUp } from 'lucide-react'
import axios from 'axios'
import { API_URL } from './config'
import VoiceAssistant from './VoiceAssistant'
import './Advisor.css'

function Advisor({ user }) {
  const [weather, setWeather] = useState(null)
  const [crops, setCrops] = useState([])
  const [strategies, setStrategies] = useState([])
  const [news, setNews] = useState([])
  const [loading, setLoading] = useState(true)
  const [showAllCrops, setShowAllCrops] = useState(false)
  const [showAllStrategies, setShowAllStrategies] = useState(false)
  const [showAllNews, setShowAllNews] = useState(false)

  useEffect(() => {
    fetchAdvisorData()
  }, [])

  const fetchAdvisorData = async () => {
    const token = localStorage.getItem('token')
    try {
      const [weatherRes, cropsRes, strategiesRes, newsRes] = await Promise.all([
        axios.get(`${API_URL}/api/advisor/weather`, { headers: { Authorization: `Bearer ${token}` } }),
        axios.get(`${API_URL}/api/advisor/crops`, { headers: { Authorization: `Bearer ${token}` } }),
        axios.get(`${API_URL}/api/advisor/strategies`, { headers: { Authorization: `Bearer ${token}` } }),
        axios.get(`${API_URL}/api/advisor/news`, { headers: { Authorization: `Bearer ${token}` } })
      ])
      setWeather(weatherRes.data)
      setCrops(cropsRes.data.crops || [])
      setStrategies(strategiesRes.data.strategies || [])
      setNews(newsRes.data.articles || [])
    } catch (err) {
      console.error('Advisor data error:', err)
    } finally {
      setLoading(false)
    }
  }

  const displayedCrops = showAllCrops ? crops : crops.slice(0, 3)
  const displayedStrategies = showAllStrategies ? strategies : strategies.slice(0, 3)
  const displayedNews = showAllNews ? news : news.slice(0, 3)

  if (loading) {
    return (
      <div className="advisor-container">
        <div className="loading-state">Loading advisor data...</div>
      </div>
    )
  }

  return (
    <div className="advisor-container">
      <VoiceAssistant user={user} />
      <div className="advisor-content">
        <div className="advisor-header">
          <h1>🌾 Farm Advisor</h1>
          <p>Personalized recommendations for your farm</p>
        </div>

        {/* Weather & Alerts */}
        <section className="advisor-section">
          <h2><Cloud size={24} /> Weather & Alerts</h2>
          {weather && (
            <div className="weather-card">
              <div className="weather-main">
                <div className="weather-location">
                  <h3>{weather.location}</h3>
                  <p>{weather.description}</p>
                </div>
                <div className="weather-stats">
                  <div className="stat">
                    <Wind size={20} />
                    <span>{weather.temperature}°C</span>
                  </div>
                  <div className="stat">
                    <Droplets size={20} />
                    <span>{weather.humidity}%</span>
                  </div>
                  <div className="stat">
                    <Cloud size={20} />
                    <span>{weather.rainfall || 'No rain'}</span>
                  </div>
                </div>
              </div>
              {weather.alerts && weather.alerts.length > 0 && (
                <div className="weather-alerts">
                  {weather.alerts.map((alert, idx) => (
                    <div key={idx} className="alert-item">
                      <AlertTriangle size={18} />
                      <span>{alert}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </section>

        {/* Agriculture News */}
        <section className="advisor-section">
          <h2><TrendingUp size={24} /> Agriculture News</h2>
          <div className="news-grid">
            {displayedNews.map((article, idx) => (
              <div key={idx} className="news-card">
                <img src={article.image} alt={article.title} className="news-image" onError={(e) => e.target.src = 'https://images.unsplash.com/photo-1592982537447-6f2a6a0a5f17?w=400'} />
                <div className="news-content">
                  <h3>{article.title}</h3>
                  <p className="news-summary">{article.summary}</p>
                  <div className="news-footer">
                    <span className="news-source">{article.source}</span>
                    <a href={article.url} target="_blank" rel="noopener noreferrer" className="news-link">
                      Read More
                    </a>
                  </div>
                </div>
              </div>
            ))}
          </div>
          {news.length > 3 && (
            <button className="explore-btn" onClick={() => setShowAllNews(!showAllNews)}>
              {showAllNews ? <><ChevronUp size={18} /> Show Less</> : <><ChevronDown size={18} /> Explore More</>}
            </button>
          )}
        </section>

        {/* Crop Recommendations */}
        <section className="advisor-section">
          <h2><Sprout size={24} /> Crop Recommendations</h2>
          <div className="crops-grid">
            {displayedCrops.map((crop, idx) => (
              <div key={idx} className="crop-card">
                <div className="crop-header">
                  <h3>{crop.name}</h3>
                  <span className="crop-score">{crop.score}% match</span>
                </div>
                <p className="crop-explanation">{crop.explanation}</p>
                <div className="crop-details">
                  <div className="detail">
                    <Droplets size={16} />
                    <span>{crop.water_requirement}</span>
                  </div>
                  <div className="detail">
                    <TrendingUp size={16} />
                    <span>{crop.yield_potential}</span>
                  </div>
                  {crop.market_price && (
                    <div className="detail">
                      <span>₹{crop.market_price}/quintal</span>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
          {crops.length > 3 && (
            <button className="explore-btn" onClick={() => setShowAllCrops(!showAllCrops)}>
              {showAllCrops ? <><ChevronUp size={18} /> Show Less</> : <><ChevronDown size={18} /> Explore More</>}
            </button>
          )}
        </section>

        {/* Farming Strategies */}
        <section className="advisor-section">
          <h2><TrendingUp size={24} /> Farming Strategies</h2>
          <div className="strategies-grid">
            {displayedStrategies.map((strategy, idx) => (
              <div key={idx} className="strategy-card">
                <h3>{strategy.name}</h3>
                <p>{strategy.explanation}</p>
                {strategy.link && (
                  <a href={strategy.link} target="_blank" rel="noopener noreferrer" className="strategy-link">
                    <ExternalLink size={16} />
                    Learn More
                  </a>
                )}
              </div>
            ))}
          </div>
          {strategies.length > 3 && (
            <button className="explore-btn" onClick={() => setShowAllStrategies(!showAllStrategies)}>
              {showAllStrategies ? <><ChevronUp size={18} /> Show Less</> : <><ChevronDown size={18} /> Explore More</>}
            </button>
          )}
        </section>
      </div>
    </div>
  )
}

export default Advisor
