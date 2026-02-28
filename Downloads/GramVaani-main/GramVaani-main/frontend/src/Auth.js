import React, { useState, useEffect } from 'react';
import { User, Phone, Lock, MapPin, Globe, Loader, ArrowRight, CheckCircle } from 'lucide-react';
import axios from 'axios';

const API_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

function Auth({ onLogin }) {
  const [isLogin, setIsLogin] = useState(true);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [step, setStep] = useState(1);
  const [otpSent, setOtpSent] = useState(false);
  const [sessionId, setSessionId] = useState('');
  const [countdown, setCountdown] = useState(0);
  
  const [formData, setFormData] = useState({
    phone: '',
    password: '',
    otp: '',
    language: 'en',
    location: ''
  });
  const [isDetectingLocation, setIsDetectingLocation] = useState(false);
  const [locationMethod, setLocationMethod] = useState('');

  useEffect(() => {
    if (countdown > 0) {
      const timer = setTimeout(() => setCountdown(countdown - 1), 1000);
      return () => clearTimeout(timer);
    }
  }, [countdown]);

  const detectPreciseLocation = async () => {
    setIsDetectingLocation(true);
    setLocationMethod('Getting GPS location...');
    
    try {
      if (navigator.geolocation) {
        const position = await new Promise((resolve, reject) => {
          navigator.geolocation.getCurrentPosition(
            resolve,
            reject,
            {
              enableHighAccuracy: true,
              timeout: 10000,
              maximumAge: 300000
            }
          );
        });
        
        const { latitude, longitude } = position.coords;
        setLocationMethod('Getting address details...');
        
        const response = await axios.post(`${API_URL}/api/reverse-geocode`, {
          latitude,
          longitude
        });
        
        if (response.data.address) {
          setFormData(prev => ({ 
            ...prev, 
            location: response.data.address
          }));
          setLocationMethod('GPS location detected');
          return;
        }
      }
    } catch (gpsError) {
      console.log('GPS location failed, trying IP location:', gpsError);
      setLocationMethod('Using IP location...');
    }
    
    try {
      const response = await axios.get(`${API_URL}/api/location`);
      if (response.data.location) {
        setFormData(prev => ({ ...prev, location: response.data.location }));
        setLocationMethod('IP-based location');
      }
    } catch (err) {
      console.error('All location detection failed:', err);
      setLocationMethod('Location detection failed');
    } finally {
      setIsDetectingLocation(false);
      setTimeout(() => setLocationMethod(''), 3000);
    }
  };

  useEffect(() => {
    if (!isLogin && step === 3) {
      detectPreciseLocation();
    }
  }, [isLogin, step]);

  const validatePhone = (phone) => {
    const pattern = /^\+91[6-9]\d{9}$/;
    return pattern.test(phone);
  };

  const formatPhoneNumber = (value) => {
    let cleaned = value.replace(/[^\d+]/g, '');
    
    if (!cleaned.startsWith('+')) {
      if (cleaned.startsWith('91')) {
        cleaned = '+' + cleaned;
      } else if (cleaned.length > 0) {
        cleaned = '+91' + cleaned;
      }
    } else if (cleaned.startsWith('+') && !cleaned.startsWith('+91')) {
      cleaned = '+91' + cleaned.substring(1);
    }
    
    if (cleaned.length > 13) {
      cleaned = cleaned.substring(0, 13);
    }
    
    return cleaned;
  };

  const handlePhoneChange = (e) => {
    const formatted = formatPhoneNumber(e.target.value);
    setFormData(prev => ({ ...prev, phone: formatted }));
  };

  const requestOTP = async () => {
    if (!validatePhone(formData.phone)) {
      setError('Please enter a valid phone number (+91 followed by 10 digits)');
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      const response = await axios.post(`${API_URL}/api/request-otp`, {
        phone: formData.phone
      });
      
      setSessionId(response.data.session_id);
      setOtpSent(true);
      setStep(2);
      setCountdown(60);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to send OTP. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const verifyOTPAndProceed = async () => {
    if (formData.otp.length !== 6) {
      setError('Please enter the 6-digit OTP');
      return;
    }

    if (isLogin) {
      await handleLogin();
    } else {
      setStep(3);
      setError('');
    }
  };

  const handleLogin = async () => {
    setIsLoading(true);
    setError('');

    try {
      const response = await axios.post(`${API_URL}/api/login`, {
        phone: formData.phone,
        password: formData.password,
        otp: formData.otp,
        session_id: sessionId
      });
      
      if (response.data.access_token) {
        localStorage.setItem('token', response.data.access_token);
        onLogin(response.data.access_token);
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed. Please check your credentials.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSignup = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    try {
      const response = await axios.post(`${API_URL}/api/signup`, {
        phone: formData.phone,
        password: formData.password,
        otp: formData.otp,
        session_id: sessionId,
        language: formData.language,
        location: formData.location
      });
      
      if (response.data.access_token) {
        localStorage.setItem('token', response.data.access_token);
        onLogin(response.data.access_token);
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Signup failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleInputChange = (e) => {
    setFormData(prev => ({
      ...prev,
      [e.target.name]: e.target.value
    }));
  };

  const resetForm = () => {
    setStep(1);
    setOtpSent(false);
    setSessionId('');
    setFormData({
      phone: '',
      password: '',
      otp: '',
      language: 'en',
      location: ''
    });
    setError('');
  };

  const switchMode = () => {
    setIsLogin(!isLogin);
    resetForm();
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <div className="auth-header">
          <div className="auth-logo">
            <div className="auth-logo-icon">🌾</div>
            <h2>Gram Vaani</h2>
          </div>
          <p className="auth-subtitle">
            {isLogin ? 'Welcome back to your AI assistant' : 'Join the rural revolution'}
          </p>
        </div>

        <div className="auth-toggle">
          <button 
            className={`auth-toggle-btn ${isLogin ? 'active' : ''}`}
            onClick={() => { setIsLogin(true); resetForm(); }}
          >
            Login
          </button>
          <button 
            className={`auth-toggle-btn ${!isLogin ? 'active' : ''}`}
            onClick={() => { setIsLogin(false); resetForm(); }}
          >
            Sign Up
          </button>
        </div>

        <div className="step-indicator">
          <div className={`step ${step >= 1 ? 'active' : ''}`}>
            <span className="step-number">1</span>
            <span className="step-label">Phone</span>
          </div>
          <div className="step-line"></div>
          <div className={`step ${step >= 2 ? 'active' : ''}`}>
            <span className="step-number">2</span>
            <span className="step-label">OTP</span>
          </div>
          {!isLogin && (
            <>
              <div className="step-line"></div>
              <div className={`step ${step >= 3 ? 'active' : ''}`}>
                <span className="step-number">3</span>
                <span className="step-label">Details</span>
              </div>
            </>
          )}
        </div>

        {step === 1 && (
          <div className="auth-form">
            <div className="form-group">
              <label className="input-label">Phone Number</label>
              <div className="input-wrapper">
                <Phone className="input-icon" size={20} />
                <input
                  type="tel"
                  name="phone"
                  placeholder="+91 98765 43210"
                  value={formData.phone}
                  onChange={handlePhoneChange}
                  required
                  className="auth-input"
                  data-testid="phone-input"
                />
              </div>
              <p className="input-hint">Enter your 10-digit mobile number with +91</p>
            </div>

            {error && <div className="auth-error" data-testid="error-message">{error}</div>}

            <button 
              type="button" 
              onClick={requestOTP} 
              disabled={isLoading || !formData.phone} 
              className="auth-submit"
              data-testid="request-otp-btn"
            >
              {isLoading ? (
                <>
                  <Loader className="loading" size={20} />
                  Sending OTP...
                </>
              ) : (
                <>
                  Get OTP <ArrowRight size={20} />
                </>
              )}
            </button>
          </div>
        )}

        {step === 2 && (
          <div className="auth-form">
            <div className="otp-sent-message">
              <CheckCircle size={20} className="success-icon" />
              OTP sent to {formData.phone}
            </div>

            <div className="form-group">
              <label className="input-label">Enter OTP</label>
              <div className="input-wrapper">
                <input
                  type="text"
                  name="otp"
                  placeholder="Enter 6-digit OTP"
                  value={formData.otp}
                  onChange={handleInputChange}
                  maxLength={6}
                  required
                  className="auth-input otp-input"
                  data-testid="otp-input"
                />
              </div>
              {countdown > 0 ? (
                <p className="input-hint">Resend OTP in {countdown}s</p>
              ) : (
                <button 
                  type="button" 
                  onClick={requestOTP} 
                  className="resend-btn"
                  disabled={isLoading}
                >
                  Resend OTP
                </button>
              )}
            </div>

            {isLogin && (
              <div className="form-group">
                <label className="input-label">Password</label>
                <div className="input-wrapper">
                  <Lock className="input-icon" size={20} />
                  <input
                    type="password"
                    name="password"
                    placeholder="Enter your password"
                    value={formData.password}
                    onChange={handleInputChange}
                    required
                    className="auth-input"
                    data-testid="password-input"
                  />
                </div>
              </div>
            )}

            {error && <div className="auth-error" data-testid="error-message">{error}</div>}

            <div className="button-group">
              <button 
                type="button" 
                onClick={() => { setStep(1); setError(''); }} 
                className="auth-back-btn"
              >
                Back
              </button>
              <button 
                type="button" 
                onClick={isLogin ? handleLogin : verifyOTPAndProceed} 
                disabled={isLoading || formData.otp.length !== 6 || (isLogin && !formData.password)} 
                className="auth-submit"
                data-testid="verify-otp-btn"
              >
                {isLoading ? (
                  <>
                    <Loader className="loading" size={20} />
                    {isLogin ? 'Logging in...' : 'Verifying...'}
                  </>
                ) : (
                  <>
                    {isLogin ? 'Login' : 'Continue'} <ArrowRight size={20} />
                  </>
                )}
              </button>
            </div>
          </div>
        )}

        {step === 3 && !isLogin && (
          <form onSubmit={handleSignup} className="auth-form">
            <div className="otp-sent-message">
              <CheckCircle size={20} className="success-icon" />
              Phone verified: {formData.phone}
            </div>

            <div className="form-group">
              <label className="input-label">Create Password</label>
              <div className="input-wrapper">
                <Lock className="input-icon" size={20} />
                <input
                  type="password"
                  name="password"
                  placeholder="Create a strong password"
                  value={formData.password}
                  onChange={handleInputChange}
                  required
                  className="auth-input"
                  data-testid="password-input"
                />
              </div>
            </div>

            <div className="form-group">
              <label className="input-label">Preferred Language</label>
              <div className="input-wrapper">
                <Globe className="input-icon" size={20} />
                <select
                  name="language"
                  value={formData.language}
                  onChange={handleInputChange}
                  className="auth-select"
                  data-testid="language-select"
                >
                  <option value="en">🇺🇸 English</option>
                  <option value="hi">🇮🇳 Hindi</option>
                  <option value="mr">🇮🇳 Marathi</option>
                  <option value="bn">🇮🇳 Bengali</option>
                  <option value="ta">🇮🇳 Tamil</option>
                  <option value="te">🇮🇳 Telugu</option>
                </select>
              </div>
            </div>

            <div className="form-group">
              <label className="input-label">Location</label>
              <div className="input-wrapper">
                <MapPin className="input-icon" size={20} />
                <input
                  type="text"
                  name="location"
                  placeholder="Location (GPS auto-detected)"
                  value={formData.location}
                  onChange={handleInputChange}
                  required
                  className="auth-input"
                  data-testid="location-input"
                />
                <button
                  type="button"
                  onClick={detectPreciseLocation}
                  disabled={isDetectingLocation}
                  className="location-btn"
                  title="Get precise GPS location"
                >
                  {isDetectingLocation ? <Loader className="loading" size={16} /> : '🎯'}
                </button>
              </div>
              {locationMethod && (
                <div className="location-status">
                  {locationMethod}
                </div>
              )}
            </div>

            {error && <div className="auth-error" data-testid="error-message">{error}</div>}

            <div className="button-group">
              <button 
                type="button" 
                onClick={() => setStep(2)} 
                className="auth-back-btn"
              >
                Back
              </button>
              <button 
                type="submit" 
                disabled={isLoading || !formData.password || !formData.location} 
                className="auth-submit"
                data-testid="signup-btn"
              >
                {isLoading ? (
                  <>
                    <Loader className="loading" size={20} />
                    Creating account...
                  </>
                ) : (
                  <>
                    <User size={20} />
                    Create Account
                  </>
                )}
              </button>
            </div>
          </form>
        )}

        <div className="auth-footer">
          <p>
            {isLogin ? "Don't have an account? " : "Already have an account? "}
            <button 
              type="button"
              onClick={switchMode}
              className="auth-link"
            >
              {isLogin ? 'Sign up' : 'Sign in'}
            </button>
          </p>
        </div>
      </div>
    </div>
  );
}

export default Auth;
