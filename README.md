# AudioProbe
<MULTIPLATFORM SUPPORT IN PROGRESS>
A Python library with a native C++ extension for FFmpeg's libavformat/libavcodec that provides a simple interface to extract audio file metadata.

## Installation

```bash
pip install audioprobe
```

## Usage

```python
from audioprobe import probe

# Extract metadata from an audio file
metadata = probe("path/to/your/audiofile.mp3")

# Access metadata properties
print(f"Duration: {metadata.duration_seconds:.2f} seconds")
print(f"File size: {metadata.file_size_bytes} bytes")
print(f"Codec: {metadata.codec_name}")
print(f"Format: {metadata.format_name}")
print(f"Audio streams: {metadata.audio_stream_count}")
print(f"Total streams: {metadata.total_stream_count}")
```

## Features

- Fast metadata extraction using native FFmpeg libraries
- Support for many audio formats including MP3, WAV, FLAC, OGG/Opus, and more
- Provides duration, file size, codec information, format details, and stream counts
- Simple Python interface with Pydantic models for type safety

## Requirements

- Python 3.6+
- FFmpeg libraries (libavformat, libavcodec, libavutil)
- C++ compiler that supports C++11

## License

This project is licensed under the MIT License - see the LICENSE file for details. 
