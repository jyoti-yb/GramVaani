import React, { useState, useRef } from 'react'
import { Mic, MicOff, Play, Pause, Loader } from 'lucide-react'
import axios from 'axios'

function App() {
  const [isRecording, setIsRecording] = useState(false)
  const [isProcessing, setIsProcessing] = useState(false)
  const [response, setResponse] = useState(null)
  const [error, setError] = useState(null)
  const [audioUrl, setAudioUrl] = useState(null)
  const [isPlaying, setIsPlaying] = useState(false)
  
  const mediaRecorderRef = useRef(null)
  const audioRef = useRef(null)
  const chunksRef = useRef([])

  const startRecording = async () => {
    try {
      setError(null)
      setResponse(null)
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
    try {
      const formData = new FormData()
      formData.append('audio_file', audioBlob, 'recording.wav')

      const response = await axios.post('http://localhost:8000/process-audio', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })

      setResponse(response.data)
      
      if (response.data.audio_url) {
        setAudioUrl(`http://localhost:8000${response.data.audio_url}`)
      }
    } catch (err) {
      setError('Failed to process audio. Please try again.')
      console.error('Error processing audio:', err)
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

  const handleAudioEnded = () => {
    setIsPlaying(false)
  }

  return (
    <div className="container">
      <div className="header">
        <h1>🌾 Gram Vaani</h1>
        <p>AI Voice Assistant for Rural India</p>
      </div>

      <div className="main-card">
        <div className="voice-section">
          <button
            className={`voice-button ${isRecording ? 'recording' : ''}`}
            onClick={isRecording ? stopRecording : startRecording}
            disabled={isProcessing}
          >
            {isProcessing ? (
              <Loader className="loading" />
            ) : isRecording ? (
              <MicOff size={40} />
            ) : (
              <Mic size={40} />
            )}
          </button>
          
          <div className="status-text">
            {isRecording 
              ? "🎤 Listening... Click to stop" 
              : isProcessing 
              ? "🤖 Processing your request..." 
              : "👆 Click to speak in your local dialect"
            }
          </div>
        </div>

        {error && (
          <div className="error-message">
            {error}
          </div>
        )}

        {response && (
          <div className="response-section">
            <h3>📝 Transcript:</h3>
            <p className="response-text">{response.transcript}</p>
            
            <h3>💬 Response:</h3>
            <p className="response-text">{response.response_text}</p>
            
            {audioUrl && (
              <div>
                <h3>🔊 Voice Response:</h3>
                <audio
                  ref={audioRef}
                  src={audioUrl}
                  onEnded={handleAudioEnded}
                  preload="auto"
                />
                <button
                  onClick={playAudio}
                  style={{
                    background: '#667eea',
                    color: 'white',
                    border: 'none',
                    padding: '10px 20px',
                    borderRadius: '25px',
                    cursor: 'pointer',
                    marginTop: '10px',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px',
                    margin: '10px auto'
                  }}
                >
                  {isPlaying ? <Pause size={16} /> : <Play size={16} />}
                  {isPlaying ? 'Pause' : 'Play'} Response
                </button>
              </div>
            )}
          </div>
        )}
      </div>

      <div className="features-grid">
        <div className="feature-card">
          <div className="feature-icon">🌤️</div>
          <div className="feature-title">Weather Information</div>
          <div className="feature-description">
            Get real-time weather updates and farming advice for your location
          </div>
        </div>

        <div className="feature-card">
          <div className="feature-icon">💰</div>
          <div className="feature-title">Crop Prices</div>
          <div className="feature-description">
            Check current market prices for your crops and get selling advice
          </div>
        </div>

        <div className="feature-card">
          <div className="feature-icon">🏛️</div>
          <div className="feature-title">Government Schemes</div>
          <div className="feature-description">
            Learn about available government schemes and how to apply
          </div>
        </div>

        <div className="feature-card">
          <div className="feature-icon">🗣️</div>
          <div className="feature-title">Multi-Dialect Support</div>
          <div className="feature-description">
            Speak in your local language - Hindi, Telugu, Punjabi, Bhojpuri, and more
          </div>
        </div>
      </div>
    </div>
  )
}

export default App
