#!/bin/bash
mkdir pricing
cp *.py pricing/
cp requirements.txt pricing/
zip -r pricing.zip pricing
rm -r pricing/
