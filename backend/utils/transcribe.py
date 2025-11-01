import subprocess
import json
import os

def transcribe_audio(file_path: str, output_dir: str = "uploads/transcripts"):
    """
    Transcribe audio using WhisperX CLI with diarization and remove 'words' & 'word_segments' fields from the result.
    
    Args:
        file_path: Path to the audio file
        output_dir: Directory where WhisperX will save the output
    
    Returns:
        dict: Parsed transcript with diarization data (without 'words' or 'word_segments')
    """
    print("transcribe called")
    os.makedirs(output_dir, exist_ok=True)

    cmd = [
        "whisperx",
        file_path,
        "--model", "medium",
        "--output_dir", output_dir,
        "--output_format", "json",
        "--diarize",
        "--language", "en",
        "--compute_type", "int8",
        "--diarize_model", "pyannote/speaker-diarization-3.0",
        "--max_speakers", "2",
    ]

    try:
        # Run WhisperX command
        subprocess.run(cmd, capture_output=True, text=True, check=True)

        # Load WhisperX output JSON
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        json_output_path = os.path.join(output_dir, f"{base_name}.json")

        if not os.path.exists(json_output_path):
            raise FileNotFoundError(f"WhisperX output not found at {json_output_path}")

        with open(json_output_path, 'r', encoding='utf-8') as f:
            transcript_data = json.load(f)

        # Remove 'words' from each segment
        if "segments" in transcript_data:
            for segment in transcript_data["segments"]:
                segment.pop("words", None)

        # Remove top-level 'word_segments' field
        transcript_data.pop("word_segments", None)

        # (Optional) overwrite cleaned JSON file
        with open(json_output_path, 'w', encoding='utf-8') as f:
            json.dump(transcript_data, f, ensure_ascii=False, indent=2)

        return transcript_data

    except subprocess.CalledProcessError as e:
        print(f"WhisperX error: {e.stderr}")
        raise Exception(f"Transcription failed: {e.stderr}")
    except Exception as e:
        print(f"Error in transcription: {str(e)}")
        raise
