FROM ubuntu:20.04

WORKDIR /opt/erp-backend

RUN apt-get update && apt-get install -y libpq-dev python3-pip

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY run.sh main.py env.py ./
COPY migrations migrations
COPY erp_backend erp_backend

ENTRYPOINT ["/bin/bash", "run.sh"]
