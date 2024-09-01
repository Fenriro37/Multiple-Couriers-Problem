FROM python:3.9-slim

WORKDIR /CDMO

RUN apt-get update && apt-get install -y \
    wget \
    tar \
    glpk-utils \
    z3 \
    libqt5widgets5 \
    libqt5printsupport5 \
    libqt5concurrent5 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN wget -O MiniZincIDE-latest-bundle-linux-x86_64.tgz https://github.com/MiniZinc/MiniZincIDE/releases/download/2.6.4/MiniZincIDE-2.6.4-bundle-linux-x86_64.tgz

RUN tar -xzf MiniZincIDE-latest-bundle-linux-x86_64.tgz --strip-components=1 -C /usr/local \
    && rm MiniZincIDE-latest-bundle-linux-x86_64.tgz

ENV PATH="/usr/local/bin:${PATH}"

RUN pip3 install minizinc numpy pulp z3-solver

COPY . .

ENTRYPOINT ["python3", "main.py"]

