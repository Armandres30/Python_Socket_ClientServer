FROM python:3.8

ENV SRC_DIR /usr/bin/src/webapp/src

COPY src/* $(SRC_DIR)/

WORKDIR $(SRC_DIR)

ENV PYTHONUNBUFFERED=!

CMD ["python", "simple_server.py"]