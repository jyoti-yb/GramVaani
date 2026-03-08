import React, { useState, useRef } from 'react'
import { Mic, MicOff, Send, X, MessageCircle, Loader } from 'lucide-react'
import axios from 'axios'
import { API_URL } from './config'
import './VoiceAssistant.css'

function VoiceAssistant({ user }) {
  const [isOpen, setIsOpen] = useState(false)
  const [messages, setMessages] = useState([])
  const [textInput, setTextInput] = useState('')
  const [isRecording, setIsRecording] = useState(false)
  const [isProcessing, setIsProcessing] = useState(false)
  const mediaRecorderRef = useRef(null)
  const chunksRef = useRef([])

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
      for (let i = 0; i < str.length; i++) {
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
    for (let i = 0; i < samples.length; i++, offset += 2) {
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

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const preferredTypes = ['audio/webm;codecs=opus', 'audio/webm', 'audio/ogg;codecs=opus', 'audio/ogg']
      const supportedType = preferredTypes.find((type) => MediaRecorder.isTypeSupported(type))
      const recorderOptions = supportedType ? { mimeType: supportedType } : undefined
      mediaRecorderRef.current = recorderOptions ? new MediaRecorder(stream, recorderOptions) : new MediaRecorder(stream)
      chunksRef.current = []
      mediaRecorderRef.current.ondataavailable = (event) => chunksRef.current.push(event.data)
      mediaRecorderRef.current.onstop = async () => {
        const audioBlob = new Blob(chunksRef.current, { type: mediaRecorderRef.current.mimeType || 'audio/webm' })
        const wavBlob = await convertToWav(audioBlob)
        await processVoice(wavBlob)
        stream.getTracks().forEach(track => track.stop())
      }
      mediaRecorderRef.current.start()
      setIsRecording(true)
    } catch (err) {
      console.error('Mic error:', err)
    }
  }

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop()
      setIsRecording(false)
    }
  }

  const processVoice = async (audioBlob) => {
    setIsProcessing(true)
    try {
      const token = localStorage.getItem('token')
      const formData = new FormData()
      formData.set('file', audioBlob, 'recording.wav')
      const res = await axios.post(`${API_URL}/api/advisor/assistant`, formData, {
        headers: { 'Content-Type': 'multipart/form-data', 'Authorization': `Bearer ${token}` }
      })
      setMessages(prev => [...prev, { type: 'user', text: res.data.transcript }, { type: 'bot', text: res.data.response }])
    } catch (err) {
      console.error('Voice error:', err)
    } finally {
      setIsProcessing(false)
    }
  }

  const sendText = async () => {
    if (!textInput.trim()) return
    const query = textInput.trim()
    setTextInput('')
    setMessages(prev => [...prev, { type: 'user', text: query }])
    setIsProcessing(true)
    try {
      const token = localStorage.getItem('token')
      const res = await axios.post(`${API_URL}/api/advisor/assistant`, { text: query }, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      setMessages(prev => [...prev, { type: 'bot', text: res.data.response }])
    } catch (err) {
      console.error('Text error:', err)
    } finally {
      setIsProcessing(false)
    }
  }

  return (
    <>
      <button className="voice-assistant-fab" onClick={() => setIsOpen(!isOpen)}>
        <MessageCircle size={24} />
        <span>Ask GramVaani</span>
      </button>

      {isOpen && (
        <div className="voice-assistant-panel">
          <div className="assistant-header">
            <h3>🌾 GramVaani Assistant</h3>
            <button onClick={() => setIsOpen(false)}><X size={20} /></button>
          </div>
          <div className="assistant-messages">
            {messages.length === 0 && (
              <div className="welcome-msg">
                <p>👋 Ask me about crops, weather, or farming strategies!</p>
              </div>
            )}
            {messages.map((msg, idx) => (
              <div key={idx} className={`message ${msg.type}`}>
                <p>{msg.text}</p>
              </div>
            ))}
            {isProcessing && (
              <div className="message bot">
                <Loader className="spinner" size={16} />
                <p>Thinking...</p>
              </div>
            )}
          </div>
          <div className="assistant-input">
            <button className={`voice-btn ${isRecording ? 'recording' : ''}`} onClick={isRecording ? stopRecording : startRecording} disabled={isProcessing}>
              {isRecording ? <MicOff size={20} /> : <Mic size={20} />}
            </button>
            <input type="text" value={textInput} onChange={(e) => setTextInput(e.target.value)} onKeyPress={(e) => e.key === 'Enter' && sendText()} placeholder="Type your question..." disabled={isProcessing} />
            <button className="send-btn" onClick={sendText} disabled={isProcessing || !textInput.trim()}>
              <Send size={20} />
            </button>
          </div>
        </div>
      )}
    </>
  )
}

export default VoiceAssistant
