FROM python
WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip install -r requirements.txt
RUN apt-get update && apt-get install -y supervisor
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY . .
ENTRYPOINT ["supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]