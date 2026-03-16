# goit-pythonweb-hw-03

## build container

```bash
docker build -t simple-http-server .
```

## run container

```bash
docker run -p 3000:3000 simple-http-server
```

server run on http://localhost:3000

## run container with volume

```bash
mkdir storage
docker run -p 3000:3000 -v $(pwd)/storage:/app/storage simple-http-server
```
