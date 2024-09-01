FROM minizinc/minizinc:latest

WORKDIR /CDMO

COPY . .

RUN apt-get update
RUN apt-get install -y python3
RUN apt-get install -y python3-pip
RUN apt-get install -y glpk-utils
RUN apt-get install -y z3

#RUN python3 -m pip install -r requirements.txt

RUN apt install -y python3-numpy
RUN apt install -y python3-pulp
RUN apt install -y python3-minizinc
RUN apt install -y python3-z3
