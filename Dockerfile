FROM ubuntu

ENV DEBIAN_FRONTEND=noninteractive 
ENV TZ=Asia/Dhaka

ENV PYTHONDONTWRITEBYTECODE=1


ENV PYTHONUNBUFFERED=1


RUN apt-get update && apt-get install -y xvfb wget curl unzip libxi6 libgconf-2-4 libxcursor1 libxss1 libxcomposite1 libasound2 libxtst6 libatk-bridge2.0-0 libgtk-3-0 python3 python3-pip fonts-liberation libgbm1 libnspr4 libnss3 libu2f-udev libvulkan1 xdg-utils scrot xdotool python3-tk python3-dev

ENV DISPLAY=:99

RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN dpkg -i google-chrome-stable_current_amd64.deb
RUN apt-get -f install -y
RUN CHROME_VERSION=$(google-chrome --version | awk '{print $3}' | awk -F "." '{print $1}') && wget -O /tmp/chromedriver.zip https://chromedriver.storage.googleapis.com/$(curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE_$CHROME_VERSION)/chromedriver_linux64.zip && unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/ && chmod +x /usr/local/bin/chromedriver

ENV DEBIAN_FRONTEND=interactive 

COPY requirements.txt .
RUN python3 -m pip install -r requirements.txt


WORKDIR /app
COPY . /app

# Creates a non-root user with an explicit UID and adds permission to access the /app folder # For more info, please refer to https://aka.ms/vscode-docker-python-configure-containers
RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

# During debugging, this entry point will be overridden
CMD xvfb-run --server-args=":99 -screen 0 800x600x16" python3 script.py
# "$FILE_PATH" "$EXPORT_FILE_NAME"
