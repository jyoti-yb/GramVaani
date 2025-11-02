const API_URL = import.meta.env.VITE_API_URL || process.env.VITE_API_URL || 'https://gramvaani-backend.onrender.com'
console.log('API_URL configured as:', API_URL)

export { API_URL }