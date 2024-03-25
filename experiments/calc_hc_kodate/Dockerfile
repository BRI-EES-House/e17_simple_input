FROM python:3.9

WORKDIR /workdir
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

RUN chmod +x ./task.sh
ENTRYPOINT ["./task.sh"]
