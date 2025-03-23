from setuptools import setup, find_packages
from pybind11.setup_helpers import Pybind11Extension, build_ext
import os
import platform
import sys

with open(os.path.join(os.path.dirname(__file__), "README.md"), encoding="utf-8") as f:
    long_description = f.read()

ffmpeg_include = ""
ffmpeg_lib = ""
extra_link_args = []
runtime_library_dirs = []

if platform.system() == "Darwin": 
    ffmpeg_include = "/opt/homebrew/Cellar/ffmpeg@6/6.1.2_8/include"
    ffmpeg_lib = "/opt/homebrew/opt/ffmpeg@6/lib"
    runtime_library_dirs = [ffmpeg_lib]
    extra_link_args = [f"-Wl,-rpath,{ffmpeg_lib}"] 
elif platform.system() == "Linux":
    ffmpeg_include = "/usr/include"
    ffmpeg_lib = "/usr/lib"
    runtime_library_dirs = [ffmpeg_lib]

if os.environ.get("FFMPEG_INCLUDE"):
    ffmpeg_include = os.environ.get("FFMPEG_INCLUDE")
if os.environ.get("FFMPEG_LIB"):
    ffmpeg_lib = os.environ.get("FFMPEG_LIB")

ext_modules = [
    Pybind11Extension(
        "audioprobe",
        ["audioprobe.cpp"],
        cxx_std=11,
        include_dirs=[ffmpeg_include],
        libraries=["avformat", "avcodec", "avutil", "swscale"],
        runtime_library_dirs=runtime_library_dirs,
        extra_link_args=extra_link_args,
    ),
]

setup(
    name="audioprobe",
    version="0.1.0",
    author="Jacek Duszenko",
    author_email="jacek@elevenlabs.io",
    description="A native binding for libavformat to get audio file metadata",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/JacekDuszenko/audioprobe",
    packages=find_packages(),
    ext_modules=ext_modules,
    cmdclass={"build_ext": build_ext},
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: C++",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    zip_safe=False,
) 