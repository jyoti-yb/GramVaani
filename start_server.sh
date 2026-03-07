#!/bin/bash

echo "Starting Gram Vaani Backend Server..."
echo "======================================="
echo ""
echo "Configuration:"
echo "- Azure OpenAI Endpoint: https://panda-openai-api.openai.azure.com/"
echo "- Deployment: gpt-4o-mini"
echo "- API Version: 2024-12-01-preview"
echo ""

cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
