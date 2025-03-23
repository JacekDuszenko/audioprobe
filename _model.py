from pydantic import BaseModel
from typing import Optional

class AudioMetadata(BaseModel):
    duration_seconds: float
    file_size_bytes: int
    bit_rate: Optional[int] = None
    sample_rate: Optional[int] = None
    channels: Optional[int] = None
    codec_name: Optional[str] = None
    format_name: Optional[str] = None
    audio_stream_count: Optional[int] = None
    total_stream_count: Optional[int] = None 