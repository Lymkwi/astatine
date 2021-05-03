#Astatine, a standalone image captioning server.

## Installation

#### Running it in a terminal

First of all, install python 3.9.
Then, install the requirements : `python3 install -r requirements.txt`
And finally, run the API : `python3 api.py`


#### Docker

Simply run the following command : `docker build . -t "astatine/latest && docker run -d -p 6969:6969 --name "whatevernameyouwant" astatine/latest`
The image uses `python:3.9-slim-buster` as a base image.