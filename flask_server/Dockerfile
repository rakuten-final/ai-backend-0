FROM python:3.10-alpine
RUN apk add --no-cache --update \
    python3 python3-dev gcc \
    gfortran musl-dev g++ \
    libffi-dev openssl-dev \
    libxml2 libxml2-dev \
    libxslt libxslt-dev \
    libjpeg-turbo-dev zlib-dev \
    linux-headers cmake libc-dev \
    make

EXPOSE 8080/tcp

WORKDIR /app

COPY requirements.txt .

# RUN pip3 install --upgrade pip
# RUN pip3 install --upgrade cython
# RUN pip install --upgrade cython
RUN pip3 install -r requirements.txt

COPY . .

CMD [ "python", "./app.py" ]