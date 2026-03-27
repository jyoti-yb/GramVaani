import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { API_URL } from './config';

const HyperlocalContext = () => {
  const [context, setContext] = useState(null);
  const [stories, setStories] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchHyperlocalData();
  }, []);

  const fetchHyperlocalData = async () => {
    try {
      const token = localStorage.getItem('token');
      const headers = { Authorization: `Bearer ${token}` };

      const contextRes = await axios.get(`${API_URL}/api/hyperlocal-context`, { headers });
      setContext(contextRes.data);

      const storiesRes = await axios.get(`${API_URL}/api/success-stories?limit=5`, { headers });
      setStories(storiesRes.data.stories);

      setLoading(false);
    } catch (error) {
      console.error('Error fetching hyperlocal data:', error);
      setLoading(false);
    }
  };

  const reportPest = async (pestName, crop, severity) => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(
        `${API_URL}/api/report-pest-outbreak`,
        null,
        {
          headers: { Authorization: `Bearer ${token}` },
          params: { pest_name: pestName, crop, severity }
        }
      );

      if (response.data.outbreak_alert) {
        alert(`⚠️ Outbreak Alert! ${response.data.nearby_reports} reports in your area`);
      } else {
        alert('✅ Pest report submitted successfully');
      }
    } catch (error) {
      console.error('Error reporting pest:', error);
    }
  };

  if (loading) return <div>Loading hyperlocal data...</div>;

  return (
    <div className="hyperlocal-container">
      {context?.has_data && (
        <div className="context-card">
          <h3>📍 Your Location Context</h3>
          <p><strong>Location:</strong> {context.location}</p>
          <p><strong>Soil Type:</strong> {context.soil_type}</p>
          <p><strong>Rainfall:</strong> {context.rainfall}</p>
          <p><strong>Current Season:</strong> {context.current_season}</p>

          <div className="recommended-crops">
            <h4>🌾 Recommended Crops</h4>
            <ul>
              {context.recommended_crops.map((crop, idx) => (
                <li key={idx}>{crop}</li>
              ))}
            </ul>
          </div>

          {context.pest_alerts.length > 0 && (
            <div className="pest-alerts">
              <h4>⚠️ Pest Alerts</h4>
              <ul>
                {context.pest_alerts.map((alert, idx) => (
                  <li key={idx} className="alert-item">{alert}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {stories.length > 0 && (
        <div className="success-stories">
          <h3>🏆 Nearby Farmer Success Stories</h3>
          {stories.map((story, idx) => (
            <div key={idx} className="story-card">
              <h4>{story.farmer}</h4>
              <p className="location">{story.location}</p>
              <p className="achievement">✨ {story.achievement}</p>
              <p className="method"><strong>Method:</strong> {story.method}</p>
            </div>
          ))}
        </div>
      )}

      <button
        className="report-pest-btn"
        onClick={() => reportPest('Fall Armyworm', 'Maize', 'high')}
      >
        🐛 Report Pest Issue
      </button>
    </div>
  );
};

export default HyperlocalContext;
