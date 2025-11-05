# Docker Commands


## creating image
docker build -t codewell-app .

## Creating container
docker run -d --name codewell-app-container -p "8080:8080" -v C:\Users\ARL\Videos\Captures\Learn\code_review\chroma_db:/codewell/codewell -e groq_api_key="WA" codewell-app

 - Incase of composer.yaml file, .env can be passed directly there

## removing container
docker rm -f f22b

## looking into logs for container
docker logs -f codewell-app-container

## Stop container
docker stop 3330(container_id)

## Start container
docker start 3330

docker images