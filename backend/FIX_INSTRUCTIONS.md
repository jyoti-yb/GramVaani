# How to Fix the 500 Internal Server Error

## Problem
Your OpenAI API key is invalid or expired, causing the audio processing to fail with a 500 error.

## Solution

### Step 1: Get a Valid OpenAI API Key
1. Visit https://platform.openai.com/api-keys
2. Sign in or create an account
3. Click "Create new secret key"
4. Copy the key (it starts with `sk-proj-` or `sk-`)

### Step 2: Update Your .env File
1. Open the `.env` file in the `backend` folder
2. Replace the current `OPENAI_API_KEY` value with your new key:
   ```
   OPENAI_API_KEY=sk-proj-YOUR_NEW_KEY_HERE
   ```
3. Save the file

### Step 3: Restart the Backend Server
1. Stop the current backend server (Ctrl+C in the terminal)
2. Start it again:
   ```bash
   cd backend
   python main.py
   ```
   Or use the batch file:
   ```bash
   start_backend_simple.bat
   ```

### Step 4: Test Again
1. Open your frontend at http://localhost:3000
2. Click the microphone button
3. Speak your query
4. The error should now be fixed!

## Note
- Make sure you have billing enabled on your OpenAI account
- Check that your API key has sufficient credits/quota
- Keep your API key secure and don't share it publicly

