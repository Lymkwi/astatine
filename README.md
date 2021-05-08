# Astatine, a standalone image captioning server.

## Introduction

Astatine is a standalone image captioning server, which includes an API and web interface. 

## HTTP Requests

The API has as many endpoints as modules. It receives multipart requests which contain the image that should be described, and depending on the endpoint some parameters. As of now, there are two endpoints :
- `/yolo` uses the YOLO algorithm, which describes the image based on the location of each detected object. The HTTP request requires one additional field, `send_result=true|false`, which indicates whether or not the client wants to receive the image with the detected objects. This module is inspired by [ultralytics/yolov5](https://github.com/ultralytics/yolov5)
- `/captioning` uses the Resnet101+Attention model, heavily inspired by [sgrvinod/a-PyTorch-Tutorial-to-Image-Captioning](https://github.com/sgrvinod/a-PyTorch-Tutorial-to-Image-Captioning). The HTTP request does not require any additional field.

The API will send back a multipart response, the field `'caption'` will return the caption the module generated for the image. Furthermore, if `send_result=true` for the YOLO endpoint, the second field will contain the processed image with the detected objects.

It is possible to test the HTTP request, using the web interface at the endpoint `/` or using a tool like curl : `curl -X POST -F "send_result=true|false" -F image=@image.jpg (-o output.jpg/-i) host:port`

## Installation

#### Running it in a terminal

First of all, install python 3.9.
Then, install the requirements : `python3 install -r requirements.txt`
And finally, run the API : `python3 api.py`

#### Docker image

Simply run the following command : 
`docker build . -t astatine/latest && docker run -d -p 6969:6969 --name "whatevernameyouwant" astatine/latest`

The image uses `python:3.9-slim-buster` as a base image.

## Using the GPU for machine learning

For NVIDIA GPUs, modules can use the CUDA library to perform the machine learning computations.

However, we're unable to properly use CUDA with Docker.

## Setting up HTTPS

There are two options :
- Putting the server behind a Reverse Proxy, which will automatically enable HTTPS requests provided the server has a SSL certificate.
- Uncomment lines 10-13 and provide the path to the files containing the server key and certificate, then add to `api.run()` the parameter `ssl_context=context`