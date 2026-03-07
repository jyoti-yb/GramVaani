import boto3


def main() -> None:
    polly = boto3.client("polly", region_name="ap-south-1")

    response = polly.synthesize_speech(
        Text="नमस्ते, यह ग्रामवाणी परीक्षण है",
        OutputFormat="mp3",
        VoiceId="Aditi",
        Engine="neural",
    )

    audio_stream = response.get("AudioStream")
    if audio_stream is None:
        raise RuntimeError("No AudioStream returned from Amazon Polly.")

    with open("output.mp3", "wb") as file_handle:
        file_handle.write(audio_stream.read())

    print("Audio generated successfully.")


if __name__ == "__main__":
    main()

