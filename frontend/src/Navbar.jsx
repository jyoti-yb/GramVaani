import React from 'react'
import { Home, Users, User, LogOut, Lightbulb } from 'lucide-react'

function Navbar({ user, activePage, onNavigate, onLogout, language }) {
  const t = (key) => {
    const translations = {
      en: { home: 'Home', advisor: 'Advisor', community: 'Community', profile: 'Profile' },
      hi: { home: 'होम', advisor: 'सलाहकार', community: 'समुदाय', profile: 'प्रोफ़ाइल' },
      te: { home: 'హోమ్', advisor: 'సలహాదారు', community: 'కమ్యూనిటీ', profile: 'ప్రొఫైల్' },
      ta: { home: 'முகப்பு', advisor: 'ஆலோசகர்', community: 'சமூகம்', profile: 'சுயவிவரம்' },
      kn: { home: 'ಮುಖಪುಟ', advisor: 'ಸಲಹೆಗಾರ', community: 'ಸಮುದಾಯ', profile: 'ಪ್ರೊಫೈಲ್' },
      ml: { home: 'ഹോം', advisor: 'ഉപദേശകൻ', community: 'കമ്മ്യൂണിറ്റി', profile: 'പ്രൊഫൈൽ' },
      bn: { home: 'হোম', advisor: 'উপদেষ্টা', community: 'কমিউনিটি', profile: 'প্রোফাইল' },
      gu: { home: 'હોમ', advisor: 'સલાહકાર', community: 'સમુદાય', profile: 'પ્રોફાઇલ' },
      mr: { home: 'होम', advisor: 'सल्लागार', community: 'समुदाय', profile: 'प्रोफाइल' }
    }
    return translations[language]?.[key] || translations.en[key]
  }

  return (
    <>
      <nav className="app-navbar">
        <div className="navbar-content">
          <div className="navbar-brand" onClick={() => onNavigate('home')}>
            <span className="navbar-icon">🌾</span>
            <span className="navbar-title">Gram Vaani</span>
          </div>
          <div className="navbar-menu">
            <button className={`nav-item ${activePage === 'home' ? 'active' : ''}`} onClick={() => onNavigate('home')}>
              <Home size={18} />
              <span>{t('home')}</span>
            </button>
            <button className={`nav-item ${activePage === 'advisor' ? 'active' : ''}`} onClick={() => onNavigate('advisor')}>
              <Lightbulb size={18} />
              <span>{t('advisor')}</span>
            </button>
            <button className={`nav-item ${activePage === 'community' ? 'active' : ''}`} onClick={() => onNavigate('community')}>
              <Users size={18} />
              <span>{t('community')}</span>
            </button>
            <button className={`nav-item ${activePage === 'profile' ? 'active' : ''}`} onClick={() => onNavigate('profile')}>
              <User size={18} />
              <span>{t('profile')}</span>
            </button>
            <div className="nav-divider"></div>
            <div className="nav-user-info">
              <span className="nav-location">📍 {user?.location?.split(',')[0]}</span>
            </div>
            <button className="nav-logout" onClick={onLogout}>
              <LogOut size={18} />
            </button>
          </div>
        </div>
      </nav>
      
      {/* Mobile Bottom Navigation */}
      <div className="mobile-bottom-nav">
        <button className={`mobile-nav-item ${activePage === 'home' ? 'active' : ''}`} onClick={() => onNavigate('home')}>
          <Home size={24} />
          <span>{t('home')}</span>
        </button>
        <button className={`mobile-nav-item ${activePage === 'advisor' ? 'active' : ''}`} onClick={() => onNavigate('advisor')}>
          <Lightbulb size={24} />
          <span>{t('advisor')}</span>
        </button>
        <button className={`mobile-nav-item ${activePage === 'community' ? 'active' : ''}`} onClick={() => onNavigate('community')}>
          <Users size={24} />
          <span>{t('community')}</span>
        </button>
        <button className={`mobile-nav-item ${activePage === 'profile' ? 'active' : ''}`} onClick={() => onNavigate('profile')}>
          <User size={24} />
          <span>{t('profile')}</span>
        </button>
      </div>
    </>
  )
}

export default Navbar
