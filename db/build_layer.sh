#!/bin/bash
set -e

echo "🚀 Building Lambda Layer for Python 3.11 on Amazon Linux 2..."

# Clean old build
rm -rf layer-output
mkdir -p layer-output/python

# Run AWS Lambda Python 3.11 Docker image (entrypoint override)
docker run --rm \
  --platform=linux/amd64 \
  --entrypoint /bin/bash \
  -v "$PWD":/asset-input \
  -v "$PWD"/layer-output:/asset-output \
  public.ecr.aws/lambda/python:3.11 \
  -c "pip install -r /asset-input/requirements.txt -t /asset-output/python"


echo "📁 Dependencies installed. Zipping layer..."

cd layer-output
zip -r layer.zip python > /dev/null
cd -

echo "✅ Layer build complete: layer-output/layer.zip"
echo "Upload this layer.zip to AWS Lambda Layer console."
