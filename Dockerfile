FROM python:3.10-bullseye

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY requirements.txt /requirements.txt

RUN pip --disable-pip-version-check install -r requirements.txt

COPY ./converter.py ./converter.py

ENTRYPOINT ["python", "-u" ,"converter.py"]