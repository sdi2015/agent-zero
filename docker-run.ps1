docker build -f DockerfileLocal -t agent-zero .
docker run --rm -it `
  -p 8000:8000 -p 3000:3000 `
  -e TZ=America/Chicago `
  -e OPENAI_API_KEY=$env:OPENAI_API_KEY `
  -v "$PWD\logs:/app/logs" `
  -v "$PWD\knowledge:/app/knowledge" `
  -v "$PWD\memory:/app/memory" `
  --name agent-zero agent-zero
