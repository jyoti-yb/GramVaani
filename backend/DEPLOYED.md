# ✅ Deployment Successful!

## Backend URL
```
https://gramvaani-backend.whiteglacier-e8ae20da.centralindia.azurecontainerapps.io
```

## Next Steps

### 1. Add Environment Variables

Run this command with your actual values:

```bash
az containerapp update \
  --name gramvaani-backend \
  --resource-group gramvaani-rg \
  --set-env-vars \
    MONGO_URL="your-mongodb-url" \
    AZURE_OPENAI_ENDPOINT="your-endpoint" \
    AZURE_OPENAI_API_KEY="your-key" \
    AZURE_OPENAI_DEPLOYMENT="gpt-4o-mini" \
    AZURE_SPEECH_KEY="your-speech-key" \
    AZURE_SPEECH_REGION="centralindia" \
    OPENWEATHER_API_KEY="your-weather-key" \
    SECRET_KEY="your-secret-key" \
    AWS_ACCESS_KEY_ID="your-aws-key" \
    AWS_SECRET_ACCESS_KEY="your-aws-secret" \
    AWS_DEFAULT_REGION="ap-south-1" \
    WHATSAPP_ACCESS_TOKEN="your-whatsapp-token" \
    WHATSAPP_PHONE_NUMBER_ID="your-phone-id" \
    WHATSAPP_VERIFY_TOKEN="your-verify-token"
```

### 2. Update Frontend

Replace all `http://localhost:8000` with:
```
https://gramvaani-backend.whiteglacier-e8ae20da.centralindia.azurecontainerapps.io
```

### 3. Test Backend

```bash
curl https://gramvaani-backend.whiteglacier-e8ae20da.centralindia.azurecontainerapps.io/health
```

### 4. View Logs

```bash
az containerapp logs show \
  --name gramvaani-backend \
  --resource-group gramvaani-rg \
  --follow
```

### 5. Update Image (After Changes)

```bash
az acr build --registry gramvaaniregistry --resource-group gramvaani-rg --image gramvaani-backend:latest --file Dockerfile .

az containerapp update \
  --name gramvaani-backend \
  --resource-group gramvaani-rg \
  --image gramvaaniregistry.azurecr.io/gramvaani-backend:latest
```

## Resources Created
- Resource Group: `gramvaani-rg`
- Container Registry: `gramvaaniregistry.azurecr.io`
- Container App: `gramvaani-backend`
- Environment: `gramvaani-env`

## Cost Estimate
- ~$10-30/month (includes free tier)
- Auto-scales: 1-3 replicas

## Cleanup (Delete Everything)
```bash
az group delete --name gramvaani-rg --yes
```
