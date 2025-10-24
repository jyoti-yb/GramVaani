import React, { useState, useRef } from 'react'
import { Mic, MicOff, Play, Pause, Loader } from 'lucide-react'
import axios from 'axios'

function App() {
  const [isRecording, setIsRecording] = useState(false)
  const [isProcessing, setIsProcessing] = useState(false)
  const [response, setResponse] = useState('')
  const [error, setError] = useState('')
  const [audioUrl, setAudioUrl] = useState(null)
  const [isPlaying, setIsPlaying] = useState(false)
  const [textInput, setTextInput] = useState('')
  const [inputMode, setInputMode] = useState('voice')
  const [language, setLanguage] = useState('en')

  const mediaRecorderRef = useRef(null)
  const audioRef = useRef(null)
  const chunksRef = useRef([])

  const startRecording = async () => {
    try {
      setError('')
      setResponse('')
      setAudioUrl(null)
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      mediaRecorderRef.current = new MediaRecorder(stream)
      chunksRef.current = []
      mediaRecorderRef.current.ondataavailable = (event) => {
        chunksRef.current.push(event.data)
      }
      mediaRecorderRef.current.onstop = async () => {
        const audioBlob = new Blob(chunksRef.current, { type: 'audio/wav' })
        await processAudio(audioBlob)
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
      const formData = new FormData()
      formData.append('file', audioBlob)
      formData.append('language', language)
      const response = await axios.post('http://localhost:8000/process-audio', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      setResponse({
        transcript: response.data.transcript,
        response_text: response.data.response_text
      })
      if (response.data.audio_data) {
        const audioBlob = new Blob([Uint8Array.from(atob(response.data.audio_data), c => c.charCodeAt(0))], { type: 'audio/wav' })
        setAudioUrl(URL.createObjectURL(audioBlob))
      }
    } catch (err) {
      setError('Failed to process audio')
      console.error(err)
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
      const response = await axios.post('http://localhost:8000/process-text', {
        text: textInput.trim(),
        language
      }, {
        headers: { 'Content-Type': 'application/json' },
      })
      setResponse({
        transcript: textInput,
        response_text: response.data.response_text || response.data
      })
      if (response.data.audio_data) {
        const audioBlob = new Blob([Uint8Array.from(atob(response.data.audio_data), c => c.charCodeAt(0))], { type: 'audio/wav' })
        setAudioUrl(URL.createObjectURL(audioBlob))
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

  // -------------------- New Feature Handlers --------------------
  const getWeather = async () => {
    const city = prompt("Enter your city:")
    if (!city) return
    try {
      const res = await axios.post('http://localhost:8000/api/weather', { city, language })
      setResponse({ transcript: city, response_text: res.data.text })
    } catch {
      setError("Unable to fetch weather.")
    }
  }

  const getCropPrice = async () => {
    const crop = prompt("Enter crop name:")
    if (!crop) return
    try {
      const res = await axios.post('http://localhost:8000/api/crop-prices', { crop })
      setResponse({ transcript: crop, response_text: res.data.text })
    } catch {
      setError("Unable to fetch crop prices.")
    }
  }

  const getGovSchemes = async () => {
    const topic = prompt("Enter topic (e.g., irrigation, fertilizer):")
    if (!topic) return
    try {
      const res = await axios.post('http://localhost:8000/api/gov-schemes', { topic })
      setResponse({ transcript: topic, response_text: res.data.text })
    } catch {
      setError("Unable to fetch government schemes.")
    }
  }

  return (
    <div className="container">
      <div className="header">
        <div className="logo">
          <div className="logo-icon">🌾</div>
          <div className="logo-text">
            <h1>Gram Vaani</h1>
            <p>AI Voice Assistant for Rural India</p>
          </div>
        </div>
      </div>

      <div className="main-card">
        <div className="input-mode-selector">
          <button className={`mode-button ${inputMode === 'voice' ? 'active' : ''}`} onClick={() => setInputMode('voice')}>🎤 Voice</button>
          <button className={`mode-button ${inputMode === 'text' ? 'active' : ''}`} onClick={() => setInputMode('text')}>✍ Text</button>
        </div>

        {inputMode === 'voice' ? (
          <div className="voice-section">
            <button className={`voice-button ${isRecording ? 'recording' : ''}`} onClick={isRecording ? stopRecording : startRecording} disabled={isProcessing}>
              {isProcessing ? <Loader className="loading" /> : isRecording ? <MicOff size={40} /> : <Mic size={40} />}
            </button>
            <div className="status-text">
              {isRecording ? "🎤 Listening... Click to stop" :
                isProcessing ? "🤖 Processing your request..." :
                  "👆 Click to speak in your local dialect"}
            </div>
          </div>
        ) : (
          <div className="text-section">
            <textarea value={textInput} onChange={(e) => setTextInput(e.target.value)} placeholder="Type your question here..." className="text-input" rows={3} disabled={isProcessing} />
            <div className="text-controls">
              <button className="submit-button" onClick={processText} disabled={isProcessing || !textInput.trim()}>
                {isProcessing ? <><Loader className="loading" size={16} /> Processing...</> : 'Submit Question'}
              </button>
              <div className="language-selector-inline">
                <div className="language-icon">🌐</div>
                <select value={language} onChange={(e) => setLanguage(e.target.value)}>
                  <option value="en">🇺🇸 English</option>
                  <option value="hi">🇮🇳 Hindi</option>
                  <option value="mr">🇮🇳 Marathi</option>
                  <option value="bn">🇮🇳 Bengali</option>
                  <option value="ta">🇮🇳 Tamil</option>
                </select>
              </div>
            </div>
          </div>
        )}

        {/* Feature buttons */}
        <div className="feature-buttons">
          <button className="feature-card" onClick={getWeather}>
            <div className="icon">🌤</div>
            <div className="title">Check Weather</div>
            <div className="description">Get real-time weather updates for your area.</div>
          </button>
          <button className="feature-card" onClick={getCropPrice}>
            <div className="icon">💰</div>
            <div className="title">Crop Prices</div>
            <div className="description">Get the latest market prices for your crops.</div>
          </button>
          <button className="feature-card" onClick={getGovSchemes}>
            <div className="icon">🏛</div>
            <div className="title">Govt Schemes</div>
            <div className="description">Learn about government schemes available to you.</div>
          </button>
          <button className="feature-card">
            <div className="icon">🗣</div>
            <div className="title">Multi-Dialect Support</div>
            <div className="description">Speak in your local language – Hindi, Telugu, Punjabi, Bhojpuri, and more.</div>
          </button>
        </div>

        {error && <div className="error-message">{error}</div>}

        {response && (
          <div className="response-section">
            <h3>📝 What you said:</h3>
            <p className="response-text">{response.transcript}</p>
            <h3>💬 Response:</h3>
            <p className="response-text">{response.response_text}</p>
            {audioUrl && (
              <div className="audio-controls">
                <button className="play-button" onClick={playAudio}>
                  {isPlaying ? <Pause size={20} /> : <Play size={20} />}
                  {isPlaying ? 'Pause' : 'Play Response'}
                </button>
                <audio ref={audioRef} src={audioUrl} onEnded={handleAudioEnded} />
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

export default App
