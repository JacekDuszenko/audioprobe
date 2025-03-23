import os
import pytest
import tempfile
import subprocess
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from audioprobe import probe

DURATIONS = [1, 3, 5, 10]

FORMATS = [
    {"name": "mp3", "ext": "mp3"},
    {"name": "opus", "ext": "ogg"},
    {"name": "flac", "ext": "flac"},
    {"name": "wav", "ext": "wav"},
    {"name": "pcm_mulaw", "ext": "wav"},
    {"name": "pcm_s16le", "ext": "wav"}
]

@pytest.fixture(scope="module")
def test_files():
    test_files_dir = tempfile.mkdtemp()
    files = {}
    
    for fmt in FORMATS:
        files[fmt["name"]] = {}
        for duration in DURATIONS:
            if fmt["name"] == "pcm_mulaw":
                output_file = os.path.join(test_files_dir, f"mulaw_{duration}s.{fmt['ext']}")
                cmd = [
                    "ffmpeg", "-f", "lavfi", "-i", f"sine=frequency=1000:duration={duration}",
                    "-acodec", "pcm_mulaw", "-ar", "8000", "-ac", "1", output_file
                ]
            elif fmt["name"] == "pcm_s16le":
                output_file = os.path.join(test_files_dir, f"pcm_{duration}s.{fmt['ext']}")
                cmd = [
                    "ffmpeg", "-f", "lavfi", "-i", f"sine=frequency=1000:duration={duration}",
                    "-acodec", "pcm_s16le", output_file
                ]
            elif fmt["name"] == "opus":
                output_file = os.path.join(test_files_dir, f"{fmt['name']}_{duration}s.{fmt['ext']}")
                cmd = [
                    "ffmpeg", "-f", "lavfi", "-i", f"sine=frequency=1000:duration={duration}",
                    "-c:a", "libopus", "-b:a", "128k", output_file
                ]
            elif fmt["name"] == "wav":
                output_file = os.path.join(test_files_dir, f"{fmt['name']}_{duration}s.{fmt['ext']}")
                cmd = [
                    "ffmpeg", "-f", "lavfi", "-i", f"sine=frequency=1000:duration={duration}",
                    "-acodec", "pcm_s16le", "-ar", "44100", "-ac", "2", output_file
                ]
            else:
                output_file = os.path.join(test_files_dir, f"{fmt['name']}_{duration}s.{fmt['ext']}")
                cmd = [
                    "ffmpeg", "-f", "lavfi", "-i", f"sine=frequency=1000:duration={duration}",
                    "-c:a", fmt["name"], output_file
                ]
            
            try:
                subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                files[fmt["name"]][duration] = output_file
            except subprocess.CalledProcessError as e:
                print(f"Warning: Could not create test file for {fmt['name']} format: {e}")
                files[fmt["name"]][duration] = None
    
    yield files
    
    for root, dirs, files in os.walk(test_files_dir, topdown=False):
        for file in files:
            os.remove(os.path.join(root, file))
        for dir in dirs:
            os.rmdir(os.path.join(root, dir))
    os.rmdir(test_files_dir)

def test_audio_durations(test_files):
    """Test that duration is correctly detected for various formats and lengths."""
    for fmt_name, durations in test_files.items():
        for expected_duration, file_path in durations.items():
            if file_path is None or not os.path.exists(file_path):
                pytest.skip(f"Test file for {fmt_name} with duration {expected_duration}s not available")
                continue
                
            metadata = probe(file_path)
            
            tolerance = 0.1
            assert abs(metadata.duration_seconds - expected_duration) <= tolerance, \
                f"Expected duration {expected_duration}s, got {metadata.duration_seconds}s for {fmt_name}"
            
            assert metadata.file_size_bytes > 0
            assert metadata.codec_name is not None
            assert metadata.format_name is not None
            assert metadata.audio_stream_count > 0
            assert metadata.total_stream_count > 0
            
            print(f"✓ {fmt_name} - {expected_duration}s - Actual: {metadata.duration_seconds:.2f}s")

def test_nonexistent_file():
    """Test error handling for non-existent files."""
    with pytest.raises(ValueError):
        probe("nonexistent_file.mp3")

def test_invalid_file():
    """Test error handling for invalid audio files."""
    with tempfile.NamedTemporaryFile(suffix=".mp3") as temp_file:
        temp_file.write(b"This is not an MP3 file")
        temp_file.flush()
        
        with pytest.raises(ValueError):
            probe(temp_file.name) 