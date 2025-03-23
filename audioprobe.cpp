#include <pybind11/pybind11.h>
#include <iostream>
#include <string>
#include <algorithm>

#ifdef __cplusplus
extern "C" {
#endif

#include <libavformat/avformat.h>
#include <libavcodec/avcodec.h>
#include <libavutil/avutil.h>
#include <libavutil/channel_layout.h>
#include <libavutil/log.h>
#include <libswscale/swscale.h>

#ifdef __cplusplus
}
#endif

#include <string>
#include <vector>
#include <map>

namespace py = pybind11;

struct AudioMetadata {
    float_t duration_seconds;
    int64_t file_size_bytes;
    std::string codec_name;
    std::string format_name;
    int audio_stream_count;
    int total_stream_count;
};

py::object probe(const std::string &file_path)
{
    av_log_set_level(AV_LOG_ERROR);
    
    AVFormatContext *format_context = avformat_alloc_context();
    AudioMetadata metadata;
    if (avformat_open_input(&format_context, file_path.c_str(), nullptr, nullptr) != 0)
    {
        std::cerr << "Failed to open file: " << file_path << std::endl;
        throw py::value_error("Failed to open file: " + file_path);
    }

    if (avformat_find_stream_info(format_context, nullptr) < 0) 
    {
        std::cerr << "Failed to find stream information" << std::endl;
        avformat_close_input(&format_context);
        throw py::value_error("Failed to find stream information");
    }

    metadata.file_size_bytes = avio_size(format_context->pb);
    metadata.format_name = format_context->iformat->name;
    metadata.total_stream_count = format_context->nb_streams;
    
    metadata.audio_stream_count = 0;
    int audio_stream_idx = -1;
    
    int64_t duration_microseconds = format_context->duration;
    if (duration_microseconds == AV_NOPTS_VALUE || duration_microseconds == 0) {
        for (unsigned int i = 0; i < format_context->nb_streams; i++) {
            AVStream *stream = format_context->streams[i];
            if (stream->codecpar->codec_type == AVMEDIA_TYPE_AUDIO) {
                metadata.audio_stream_count++;
                
                if (audio_stream_idx == -1) {
                    audio_stream_idx = i;
                }
                
                if (stream->duration != AV_NOPTS_VALUE) {
                    duration_microseconds = av_rescale_q(
                        stream->duration, 
                        stream->time_base, 
                        AV_TIME_BASE_Q
                    );
                    break;
                }
            }
        }
    } else {
        for (unsigned int i = 0; i < format_context->nb_streams; i++) {
            AVStream *stream = format_context->streams[i];
            if (stream->codecpar->codec_type == AVMEDIA_TYPE_AUDIO) {
                metadata.audio_stream_count++;
                if (audio_stream_idx == -1) {
                    audio_stream_idx = i;
                }
            }
        }
    }
    
    if (audio_stream_idx >= 0) {
        AVStream *audio_stream = format_context->streams[audio_stream_idx];
        AVCodecParameters *codecpar = audio_stream->codecpar;
        
        // Get codec name
        const AVCodecDescriptor *codec_desc = avcodec_descriptor_get(codecpar->codec_id);
        if (codec_desc) {
            metadata.codec_name = codec_desc->name;
        } else {
            metadata.codec_name = "unknown";
        }
    }

    metadata.duration_seconds = duration_microseconds / 1000000.0f;
    avformat_close_input(&format_context);
    
    if (duration_microseconds == AV_NOPTS_VALUE || duration_microseconds <= 0) {
        throw py::value_error("Could not determine audio duration");
    }
    
    py::module_ metadata_module = py::module_::import("_model");
    py::object PyAudioMetadata = metadata_module.attr("AudioMetadata");
    
    py::dict kwargs;
    kwargs["duration_seconds"] = metadata.duration_seconds;
    kwargs["file_size_bytes"] = metadata.file_size_bytes;
    kwargs["codec_name"] = metadata.codec_name;
    kwargs["format_name"] = metadata.format_name;
    kwargs["audio_stream_count"] = metadata.audio_stream_count;
    kwargs["total_stream_count"] = metadata.total_stream_count;
    
    return PyAudioMetadata(**kwargs);
}

PYBIND11_MODULE(audioprobe, m)
{
    m.doc() = "Module that provides functions to get file metadata from filesystem or from bytes.";
    m.def("probe", &probe, "Check audio file metadata and return a Pydantic model",
          py::arg("file_path"));
    py::module_ models = py::module_::import("_model");
    py::object PyAudioMetadata = models.attr("AudioMetadata");
    m.attr("AudioMetadata") = PyAudioMetadata;
}