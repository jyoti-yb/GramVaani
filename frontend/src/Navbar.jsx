import React from 'react'
import { User, Users, Lightbulb, LogOut, Home } from 'lucide-react'
import { getTranslation } from './translations'
import './Navbar.css'

function Navbar({ user, currentPage, onNavigate, onLogout, language }) {
  const t = (key) => getTranslation(language || 'en', key)

  return (
    <>
      {/* Desktop Navbar */}
      <nav className="app-navbar desktop-navbar">
        <div className="navbar-content">
          <div className="navbar-brand" onClick={() => onNavigate('home')}>
            <span className="navbar-icon">🌾</span>
            <span className="navbar-title">Gram Vaani</span>
          </div>
          <div className="navbar-menu">
            <button 
              className={`nav-item ${currentPage === 'home' ? 'active' : ''}`} 
              onClick={() => onNavigate('home')}
            >
              <span>{t('home')}</span>
            </button>
            <button 
              className={`nav-item ${currentPage === 'advisor' ? 'active' : ''}`} 
              onClick={() => onNavigate('advisor')}
            >
              <Lightbulb size={18} />
              <span>{t('advisor')}</span>
            </button>
            <button 
              className={`nav-item ${currentPage === 'community' ? 'active' : ''}`} 
              onClick={() => onNavigate('community')}
            >
              <Users size={18} />
              <span>{t('community')}</span>
            </button>
            <button 
              className={`nav-item ${currentPage === 'profile' ? 'active' : ''}`} 
              onClick={() => onNavigate('profile')}
            >
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

      {/* Mobile Top Bar */}
      <nav className="app-navbar mobile-top-bar">
        <div className="navbar-content">
          <div className="navbar-brand" onClick={() => onNavigate('home')}>
            <span className="navbar-icon">🌾</span>
            <span className="navbar-title">Gram Vaani</span>
          </div>
          <button className="nav-logout" onClick={onLogout}>
            <LogOut size={20} />
          </button>
        </div>
      </nav>

      {/* Mobile Bottom Navigation */}
      <nav className="mobile-bottom-nav">
        <button 
          className={`bottom-nav-item ${currentPage === 'home' ? 'active' : ''}`}
          onClick={() => onNavigate('home')}
        >
          <Home size={24} />
          <span>{t('home')}</span>
        </button>
        <button 
          className={`bottom-nav-item ${currentPage === 'advisor' ? 'active' : ''}`}
          onClick={() => onNavigate('advisor')}
        >
          <Lightbulb size={24} />
          <span>{t('advisor')}</span>
        </button>
        <button 
          className={`bottom-nav-item ${currentPage === 'community' ? 'active' : ''}`}
          onClick={() => onNavigate('community')}
        >
          <Users size={24} />
          <span>{t('community')}</span>
        </button>
        <button 
          className={`bottom-nav-item ${currentPage === 'profile' ? 'active' : ''}`}
          onClick={() => onNavigate('profile')}
        >
          <User size={24} />
          <span>{t('profile')}</span>
        </button>
      </nav>
    </>
  )
}

export default Navbar
