FROM minizinc/minizinc:latest
FROM minizinc/minizinc:latest

WORKDIR /CDMO

COPY . .

# List contents of /CDMO
RUN ls -l /CDMO

# Start an interactive shell to inspect the container
RUN /bin/bash -c "echo 'Inspect the container. Press Ctrl+D to exit and continue the build.'; /bin/bash"


RUN apt-get update
RUN apt-get install -y python3
RUN apt-get install -y python3-pip
RUN apt-get install -y glpk-utils

#RUN apt-get install -y build-essential libssl-dev libffi-dev python3-dev
#COPY requirements.txt .

#RUN python3 -m pip install -r requirements.txt

#RUN apt install -y python3-numpy
#RUN apt install -y python3-pulp


