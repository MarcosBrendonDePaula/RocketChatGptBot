FROM python:3.11-alpine
WORKDIR /usr/src/app
ENV OPENAI_API_KEY=${OPENAI_API_KEY}
ENV BOT_NAME=${BOT_NAME}
ENV BOT_PASS=${BOT_PASS}
ENV ROCKET_URL=${ROCKET_URL}
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . ./
CMD [ "python", "./main.py" ]