FROM python:3
COPY . /app
WORKDIR /app
RUN apt-get update && apt-get install -yq python3-pygame libasound2-dev&& pip install -r requirements.txt
VOLUME /app/sounds
ENTRYPOINT ["python","core.py"]

