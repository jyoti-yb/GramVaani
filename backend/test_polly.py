import boto3

polly = boto3.client("polly", region_name="ap-south-1")

response = polly.synthesize_speech(
    Text="नमस्ते, यह ग्रामवाणी परीक्षण है",
    OutputFormat="mp3",
    VoiceId="Aditi"
)

with open("output.mp3", "wb") as f:
    f.write(response["AudioStream"].read())

print("Audio generated successfully.")
