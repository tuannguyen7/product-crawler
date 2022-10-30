#!/bin/sh

docker build . -t product-crawler:0.1
docker run -d --name product-crawler0.1 product-crawler:0.1

