# This is a weather app from example how connect to Claude Desktop


## Dockerfile

```bash
docker build -t weather .
docker run -p 8000:8000 weather
```

## Docker Compose
```bash
docker-compose up --build -d 
docker-compose logs -f
```

# Configuration of Claude Desktop
## CLAUDE Desktop via npx

{
  "mcpServers": {
    "weather": {
      "command": "C:\\Program Files\\nodejs\\npx",
      "args": [
        "-y",
        "mcp-remote",
        "http://127.0.0.1:8000/mcp"
      ]
    }
  }
}

## CLAUDE Desktop via cli 
{
  "mcpServers": {
    "weather": {
      "command": "uv",
      "args": [
        "--directory",
        "C:\\ABSOLUTE\\PATH\\TO\\PARENT\\FOLDER\\weather\src",
        "run",
        "weather.py",
      ]
    }
  }
}