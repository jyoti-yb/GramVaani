import React, { useState, useRef, useEffect } from 'react'
import { Mic, MicOff, Play, Pause, Loader, LogOut, User, Award } from 'lucide-react'
import axios from 'axios'
import Auth from './Auth'
import Profile from './Profile'
import Landing from './Landing'
import Features from './Features'
import { API_URL } from './config'
import { getTranslation } from './translations'

function App() {
  const [showLanding, setShowLanding] = useState(true)
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [user, setUser] = useState(null)
  const [isRecording, setIsRecording] = useState(false)
  const [isProcessing, setIsProcessing] = useState(false)
  const [response, setResponse] = useState('')
  const [error, setError] = useState('')
  const [audioUrl, setAudioUrl] = useState(null)
  const [isPlaying, setIsPlaying] = useState(false)
  const [textInput, setTextInput] = useState('')
  const [inputMode, setInputMode] = useState('voice')
  const [language, setLanguage] = useState('en')
  const [showModal, setShowModal] = useState(false)
  const [modalType, setModalType] = useState('')
  const [modalInput, setModalInput] = useState('')
  const [modalLocation, setModalLocation] = useState('')
  const [showProfile, setShowProfile] = useState(false)
  const [showFeatures, setShowFeatures] = useState(false)

  const mediaRecorderRef = useRef(null)
  const audioRef = useRef(null)
  const chunksRef = useRef([])
  const recorderMimeTypeRef = useRef('')

  const encodeWav = (audioBuffer) => {
    const numChannels = 1
    const sampleRate = audioBuffer.sampleRate
    const format = 1
    const bitDepth = 16

    const samples = audioBuffer.getChannelData(0)
    const blockAlign = numChannels * (bitDepth / 8)
    const byteRate = sampleRate * blockAlign
    const dataSize = samples.length * (bitDepth / 8)

    const buffer = new ArrayBuffer(44 + dataSize)
    const view = new DataView(buffer)

    const writeString = (offset, str) => {
      for (let i = 0; i < str.length; i += 1) {
        view.setUint8(offset + i, str.charCodeAt(i))
      }
    }

    writeString(0, 'RIFF')
    view.setUint32(4, 36 + dataSize, true)
    writeString(8, 'WAVE')
    writeString(12, 'fmt ')
    view.setUint32(16, 16, true)
    view.setUint16(20, format, true)
    view.setUint16(22, numChannels, true)
    view.setUint32(24, sampleRate, true)
    view.setUint32(28, byteRate, true)
    view.setUint16(32, blockAlign, true)
    view.setUint16(34, bitDepth, true)
    writeString(36, 'data')
    view.setUint32(40, dataSize, true)

    let offset = 44
    for (let i = 0; i < samples.length; i += 1, offset += 2) {
      let s = Math.max(-1, Math.min(1, samples[i]))
      s = s < 0 ? s * 0x8000 : s * 0x7fff
      view.setInt16(offset, s, true)
    }

    return buffer
  }

  const convertToWav = async (audioBlob) => {
    const arrayBuffer = await audioBlob.arrayBuffer()
    const audioContext = new (window.AudioContext || window.webkitAudioContext)()
    const decodedBuffer = await audioContext.decodeAudioData(arrayBuffer)

    const targetSampleRate = 16000
    const offlineContext = new OfflineAudioContext(1, Math.ceil(decodedBuffer.duration * targetSampleRate), targetSampleRate)
    const source = offlineContext.createBufferSource()
    source.buffer = decodedBuffer
    source.connect(offlineContext.destination)
    source.start(0)
    const renderedBuffer = await offlineContext.startRendering()

    const wavBuffer = encodeWav(renderedBuffer)
    return new Blob([wavBuffer], { type: 'audio/wav' })
  }

  useEffect(() => {
    checkAuthStatus()
  }, [])

  useEffect(() => {
    // If user is authenticated, skip landing page
    if (isAuthenticated) {
      setShowLanding(false)
    }
  }, [isAuthenticated])

  const t = (key) => getTranslation(user?.language || 'en', key)

  const checkAuthStatus = async () => {
    const token = localStorage.getItem('token')
    if (token) {
      try {
        const response = await axios.get(`${API_URL}/api/me`, {
          headers: { Authorization: `Bearer ${token}` }
        })
        setUser(response.data)
        setLanguage(response.data.language)
        setIsAuthenticated(true)
      } catch (error) {
        localStorage.removeItem('token')
        setIsAuthenticated(false)
      }
    }
  }

  const handleLogin = async (token) => {
    try {
      const response = await axios.get(`${API_URL}/api/me`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      setUser(response.data)
      setLanguage(response.data.language)
      setIsAuthenticated(true)
    } catch (error) {
      localStorage.removeItem('token')
    }
  }

  const handleLogout = () => {
    localStorage.removeItem('token')
    setIsAuthenticated(false)
    setUser(null)
    setResponse('')
    setError('')
    setAudioUrl(null)
  }

  const startRecording = async () => {
    try {
      setError('')
      setResponse('')
      setAudioUrl(null)
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })

      const preferredTypes = [
        'audio/webm;codecs=opus',
        'audio/webm',
        'audio/ogg;codecs=opus',
        'audio/ogg'
      ]
      const supportedType = preferredTypes.find((type) => MediaRecorder.isTypeSupported(type))
      const recorderOptions = supportedType ? { mimeType: supportedType } : undefined

      mediaRecorderRef.current = recorderOptions ? new MediaRecorder(stream, recorderOptions) : new MediaRecorder(stream)
      recorderMimeTypeRef.current = mediaRecorderRef.current.mimeType || supportedType || ''
      chunksRef.current = []
      mediaRecorderRef.current.ondataavailable = (event) => {
        chunksRef.current.push(event.data)
      }
      mediaRecorderRef.current.onstop = async () => {
        const chunkType = chunksRef.current[0]?.type
        const mimeType = recorderMimeTypeRef.current || chunkType || 'audio/webm'
        const audioBlob = new Blob(chunksRef.current, { type: mimeType })
        const wavBlob = await convertToWav(audioBlob)
        await processAudio(wavBlob)
        stream.getTracks().forEach(track => track.stop())
      }
      mediaRecorderRef.current.start()
      setIsRecording(true)
    } catch (err) {
      setError('Microphone access denied. Please allow microphone access and try again.')
    }
  }

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop()
      setIsRecording(false)
    }
  }

  const processAudio = async (audioBlob) => {
    setIsProcessing(true)
    setError('')
    try {
      const token = localStorage.getItem('token')
      const formData = new FormData()
      formData.set('file', audioBlob, 'recording.wav')

      console.log('Sending audio with language:', language)
      
      const response = await axios.post(`${API_URL}/process-audio?language=${language}`, formData, {
        headers: { 
          'Content-Type': 'multipart/form-data',
          'Authorization': `Bearer ${token}`
        },
      })
      setResponse({
        transcript: response.data.transcript,
        response_text: response.data.response_text
      })
      if (response.data.audio_data) {
        const audioBlob = new Blob([Uint8Array.from(atob(response.data.audio_data), c => c.charCodeAt(0))], { type: 'audio/wav' })
        const audioUrl = URL.createObjectURL(audioBlob)
        setAudioUrl(audioUrl)
        // Auto-play audio after setting URL
        setTimeout(() => {
          if (audioRef.current) {
            audioRef.current.play()
            setIsPlaying(true)
          }
        }, 100)
      }
    } catch (err) {
      const errorMessage = err.response?.data?.detail || 'Failed to process audio'
      setError(errorMessage)
      console.error('Error processing audio:', err)
    } finally {
      setIsProcessing(false)
    }
  }

  const processText = async () => {
    if (!textInput.trim()) {
      setError('Please enter some text to process.')
      return
    }
    setIsProcessing(true)
    setError('')
    setResponse('')
    setAudioUrl(null)
    try {
      const token = localStorage.getItem('token')
      const response = await axios.post(`${API_URL}/process-text`, {
        text: textInput.trim(),
        language
      }, {
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
      })
      setResponse({
        transcript: textInput,
        response_text: response.data.response_text || response.data
      })
      if (response.data.audio_data) {
        const audioBlob = new Blob([Uint8Array.from(atob(response.data.audio_data), c => c.charCodeAt(0))], { type: 'audio/wav' })
        const audioUrl = URL.createObjectURL(audioBlob)
        setAudioUrl(audioUrl)
        // Auto-play audio after setting URL
        setTimeout(() => {
          if (audioRef.current) {
            audioRef.current.play()
            setIsPlaying(true)
          }
        }, 100)
      }
    } catch (err) {
      const errorMessage = err.response?.data?.detail || 'Failed to process text. Please try again.'
      setError(errorMessage)
      console.error('Error processing text:', err)
    } finally {
      setIsProcessing(false)
    }
  }

  const playAudio = () => {
    if (audioRef.current) {
      if (isPlaying) {
        audioRef.current.pause()
        setIsPlaying(false)
      } else {
        audioRef.current.play()
        setIsPlaying(true)
      }
    }
  }

  const handleAudioEnded = () => setIsPlaying(false)

  // -------------------- Modal Handlers --------------------
  const openModal = (type) => {
    setModalType(type)
    // Pre-fill user's city for weather
    if (type === 'weather' && user?.location) {
      const city = user.location.split(',')[0].trim()
      setModalInput(city)
    } else {
      setModalInput('')
    }
    // Pre-fill user's location for crop prices
    if (type === 'crop' && user?.location) {
      setModalLocation(user.location)
    } else {
      setModalLocation('')
    }
    setShowModal(true)
  }

  // Quick access functions that use user's location automatically
  const getMyWeather = async () => {
    setIsProcessing(true)
    setError('')
    setResponse('')
    setAudioUrl(null)
    
    try {
      const token = localStorage.getItem('token')
      const res = await axios.post(`${API_URL}/api/weather`, { 
        city: 'current', // This will use user's location from profile
        language 
      }, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      
      setResponse({ 
        transcript: `Weather for my location (${user?.location})`, 
        response_text: res.data.text 
      })
      
      if (res.data.audio_data) {
        const audioBlob = new Blob([Uint8Array.from(atob(res.data.audio_data), c => c.charCodeAt(0))], { type: 'audio/wav' })
        const audioUrl = URL.createObjectURL(audioBlob)
        setAudioUrl(audioUrl)
        setTimeout(() => {
          if (audioRef.current) {
            audioRef.current.play()
            setIsPlaying(true)
          }
        }, 100)
      }
    } catch (err) {
      setError('Unable to fetch weather information for your location.')
    } finally {
      setIsProcessing(false)
    }
  }

  const getCropPricesForMyArea = (cropName) => {
    return async () => {
      setIsProcessing(true)
      setError('')
      setResponse('')
      setAudioUrl(null)
      
      try {
        const token = localStorage.getItem('token')
        const res = await axios.post(`${API_URL}/api/crop-prices`, { 
          crop: cropName,
          language 
          // market will automatically use user's location from profile
        }, {
          headers: { 'Authorization': `Bearer ${token}` }
        })
        
        setResponse({ 
          transcript: `${cropName} prices in my area (${user?.location})`, 
          response_text: res.data.text 
        })
        
        if (res.data.audio_data) {
          const audioBlob = new Blob([Uint8Array.from(atob(res.data.audio_data), c => c.charCodeAt(0))], { type: 'audio/wav' })
          const audioUrl = URL.createObjectURL(audioBlob)
          setAudioUrl(audioUrl)
          setTimeout(() => {
            if (audioRef.current) {
              audioRef.current.play()
              setIsPlaying(true)
            }
          }, 100)
        }
      } catch (err) {
        setError(`Unable to fetch ${cropName} prices for your area.`)
      } finally {
        setIsProcessing(false)
      }
    }
  }

  const closeModal = () => {
    setShowModal(false)
    setModalInput('')
    setModalLocation('')
  }

  const handleModalSubmit = async () => {
    if (!modalInput.trim()) return
    setShowModal(false)
    setIsProcessing(true)
    
    try {
      const token = localStorage.getItem('token')
      let res
      if (modalType === 'weather') {
        res = await axios.post(`${API_URL}/api/weather`, { city: modalInput, language }, {
          headers: { 'Authorization': `Bearer ${token}` }
        })
      } else if (modalType === 'crop') {
        res = await axios.post(`${API_URL}/api/crop-prices`, { 
          crop: modalInput, 
          market: modalLocation || undefined,
          language 
        }, {
          headers: { 'Authorization': `Bearer ${token}` }
        })
      } else if (modalType === 'schemes') {
        res = await axios.post(`${API_URL}/api/gov-schemes`, { topic: modalInput, language }, {
          headers: { 'Authorization': `Bearer ${token}` }
        })
      }
      setResponse({ transcript: modalInput, response_text: res.data.text })
      if (res.data.audio_data) {
        const audioBlob = new Blob([Uint8Array.from(atob(res.data.audio_data), c => c.charCodeAt(0))], { type: 'audio/wav' })
        const audioUrl = URL.createObjectURL(audioBlob)
        setAudioUrl(audioUrl)
        // Auto-play audio after setting URL
        setTimeout(() => {
          if (audioRef.current) {
            audioRef.current.play()
            setIsPlaying(true)
          }
        }, 100)
      }
    } catch {
      setError(`Unable to fetch ${modalType} information.`)
    } finally {
      setIsProcessing(false)
      setModalInput('')
      setModalLocation('')
    }
  }

  if (showLanding && !isAuthenticated) {
    return <Landing onGetStarted={() => setShowLanding(false)} />
  }

  if (!isAuthenticated) {
    return <Auth onLogin={handleLogin} />
  }

  if (!user) {
    return <div className="container"><div className="main-card">Loading...</div></div>
  }

  if (showProfile) {
    return (
      <Profile 
        user={user} 
        onBack={() => setShowProfile(false)}
        onUserUpdate={(updatedUser) => setUser({...user, ...updatedUser})}
        onLogout={handleLogout}
        onNavigate={(page) => {
          if (page === 'home') { setShowProfile(false); setShowFeatures(false); }
          else if (page === 'features') { setShowProfile(false); setShowFeatures(true); }
        }}
      />
    )
  }

  if (showFeatures) {
    return (
      <Features 
        onBack={() => setShowFeatures(false)}
        user={user}
        onLogout={handleLogout}
        onNavigate={(page) => {
          if (page === 'home') { setShowProfile(false); setShowFeatures(false); }
          else if (page === 'profile') { setShowProfile(true); setShowFeatures(false); }
        }}
      />
    )
  }

  return (
    <div className="container" key={user?.language}>
      <nav className="app-navbar">
        <div className="navbar-content">
          <div className="navbar-brand" onClick={() => { setShowProfile(false); setShowFeatures(false); }}>
            <span className="navbar-icon">🌾</span>
            <span className="navbar-title">Gram Vaani</span>
          </div>
          <div className="navbar-menu">
            <button className="nav-item" onClick={() => { setShowProfile(false); setShowFeatures(false); }}>
              <span>Home</span>
            </button>
            <button className="nav-item" onClick={() => setShowFeatures(true)}>
              <Award size={18} />
              <span>Features</span>
            </button>
            <button className="nav-item" onClick={() => setShowProfile(true)}>
              <User size={18} />
              <span>Profile</span>
            </button>
            <div className="nav-divider"></div>
            <div className="nav-user-info">
              <span className="nav-location">📍 {user?.location?.split(',')[0]}</span>
            </div>
            <button className="nav-logout" onClick={handleLogout}>
              <LogOut size={18} />
            </button>
          </div>
        </div>
      </nav>

      <div className="main-card">
        <div className="input-mode-selector">
          <button className={`mode-button ${inputMode === 'voice' ? 'active' : ''}`} onClick={() => setInputMode('voice')}>🎤 {t('voice')}</button>
          <button className={`mode-button ${inputMode === 'text' ? 'active' : ''}`} onClick={() => setInputMode('text')}>✍ {t('text')}</button>
        </div>

        {inputMode === 'voice' ? (
          <div className="voice-section">
            <button className={`voice-button ${isRecording ? 'recording' : ''}`} onClick={isRecording ? stopRecording : startRecording} disabled={isProcessing}>
              {isProcessing ? <Loader className="loading" /> : isRecording ? <MicOff size={40} /> : <Mic size={40} />}
            </button>
            <div className="status-text">
              {isRecording ? `🎤 ${t('listening')}` :
                isProcessing ? `🤖 ${t('processing')}` :
                  `👆 ${t('clickToSpeak')}`}
            </div>
            <div className="language-selector-inline">
              <div className="language-icon">🌐</div>
              <select value={language} onChange={(e) => setLanguage(e.target.value)}>
                <option value="en">🇺🇸 English</option>
                <option value="hi">🇮🇳 Hindi</option>
                <option value="ta">🇮🇳 Tamil</option>
                <option value="te">🇮🇳 Telugu</option>
                <option value="kn">🇮🇳 Kannada</option>
                <option value="ml">🇮🇳 Malayalam</option>
                <option value="bn">🇮🇳 Bengali</option>
                <option value="gu">🇮🇳 Gujarati</option>
                <option value="mr">🇮🇳 Marathi</option>
              </select>
            </div>
          </div>
        ) : (
          <div className="text-section">
            <textarea value={textInput} onChange={(e) => setTextInput(e.target.value)} placeholder={t('typeQuestion')} className="text-input" rows={3} disabled={isProcessing} />
            <div className="text-controls">
              <button className="submit-button" onClick={processText} disabled={isProcessing || !textInput.trim()}>
                {isProcessing ? <><Loader className="loading" size={16} /> {t('processing')}</> : t('submit')}
              </button>
              <div className="language-selector-inline">
                <div className="language-icon">🌐</div>
                <select value={language} onChange={(e) => setLanguage(e.target.value)}>
                  <option value="en">🇺🇸 English</option>
                  <option value="hi">🇮🇳 Hindi</option>
                  <option value="ta">🇮🇳 Tamil</option>
                  <option value="te">🇮🇳 Telugu</option>
                  <option value="kn">🇮🇳 Kannada</option>
                  <option value="ml">🇮🇳 Malayalam</option>
                  <option value="bn">🇮🇳 Bengali</option>
                  <option value="gu">🇮🇳 Gujarati</option>
                  <option value="mr">🇮🇳 Marathi</option>
                </select>
              </div>
            </div>
          </div>
        )}

        {error && <div className="error-message">{error}</div>}

        {response && (
          <div className="response-section">
            <h3>📝 {t('whatYouSaid')}</h3>
            <p className="response-text">{response.transcript}</p>
            <h3>💬 {t('response')}</h3>
            <p className="response-text">{response.response_text}</p>
            {audioUrl && (
              <div className="audio-controls">
                <button className="play-button" onClick={playAudio}>
                  {isPlaying ? <Pause size={20} /> : <Play size={20} />}
                  {isPlaying ? t('pause') : t('playResponse')}
                </button>
                <audio ref={audioRef} src={audioUrl} onEnded={handleAudioEnded} />
              </div>
            )}
          </div>
        )}

        {/* Quick Access Buttons */}
        <div className="feature-buttons">
          <button className="feature-card" onClick={getMyWeather} disabled={isProcessing}>
            <div className="icon">🌤</div>
            <div className="title">{t('myWeather')}</div>
            <div className="description">{t('currentWeather')} {user?.location?.split(',')[0] || t('yourLocation')}</div>
          </button>
          {/* <button className="feature-card" onClick={getCropPricesForMyArea('Rice')} disabled={isProcessing}>
            <div className="icon">🌾</div>
            <div className="title">Rice Prices</div>
            <div className="description">Latest rice prices in your area</div>
          </button>
          <button className="feature-card" onClick={getCropPricesForMyArea('Wheat')} disabled={isProcessing}>
            <div className="icon">🌾</div>
            <div className="title">Wheat Prices</div>
            <div className="description">Latest wheat prices in your area</div>
          </button> */}
        {/* </div> */}

        {/* More Options */}
        {/* <div className="feature-buttons" style={{marginTop: '20px'}}> */}
          <button className="feature-card" onClick={() => openModal('weather')}>
            <div className="icon">🌍</div>
            <div className="title">{t('otherCity')}</div>
            <div className="description">{t('checkWeather')}</div>
          </button>
          <button className="feature-card" onClick={() => openModal('crop')}>
            <div className="icon">💰</div>
            <div className="title">{t('cropPrices')}</div>
            <div className="description">{t('checkPrices')}</div>
          </button>
          <button className="feature-card" onClick={() => openModal('schemes')}>
            <div className="icon">🏛</div>
            <div className="title">{t('govSchemes')}</div>
            <div className="description">{t('learnSchemes')}</div>
          </button>
        </div>
      </div>

      {/* Modal */}
      {showModal && (
        <div className="modal-overlay" onClick={closeModal}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>
                {modalType === 'weather' && '🌤 Weather Information'}
                {modalType === 'crop' && '💰 Crop Prices'}
                {modalType === 'schemes' && '🏛 Government Schemes'}
              </h3>
              <button className="close-button" onClick={closeModal}>×</button>
            </div>
            <div className="modal-body">
              <label>
                {modalType === 'weather' && 'Enter city name:'}
                {modalType === 'crop' && 'Enter crop name:'}
                {modalType === 'schemes' && 'Enter topic (e.g., irrigation, fertilizer):'}
              </label>
              <input
                type="text"
                value={modalInput}
                onChange={(e) => setModalInput(e.target.value)}
                placeholder={
                  modalType === 'weather' ? 'e.g., Delhi, Mumbai, Bangalore' :
                  modalType === 'crop' ? 'e.g., Rice, Wheat, Cotton, Sugarcane' :
                  'e.g., Irrigation, Seeds, Fertilizer, Loan'
                }
                onKeyPress={(e) => e.key === 'Enter' && handleModalSubmit()}
                autoFocus
              />
              {modalType === 'crop' && (
                <>
                  <label style={{marginTop: '15px', display: 'block'}}>
                    Location (market):
                  </label>
                  <input
                    type="text"
                    value={modalLocation}
                    onChange={(e) => setModalLocation(e.target.value)}
                    placeholder="e.g., Delhi, Mumbai (defaults to your location)"
                    onKeyPress={(e) => e.key === 'Enter' && handleModalSubmit()}
                  />
                </>
              )}
              {modalType === 'weather' && (
                <p style={{fontSize: '12px', color: '#666', marginTop: '8px'}}>
                  💡 Tip: Use "My Weather" button above for your location ({user?.location})
                </p>
              )}
              {modalType === 'crop' && (
                <p style={{fontSize: '12px', color: '#666', marginTop: '8px'}}>
                  💡 Location defaults to: {user?.location || 'your profile location'}
                </p>
              )}
            </div>
            <div className="modal-footer">
              <button className="cancel-button" onClick={closeModal}>Cancel</button>
              <button className="submit-button" onClick={handleModalSubmit} disabled={!modalInput.trim()}>Get Information</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default App
