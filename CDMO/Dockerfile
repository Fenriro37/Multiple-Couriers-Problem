# # Start with an official Python 3 image
# FROM python:3.9-slim

# # Set the working directory inside the container
# WORKDIR /CDMO

# # Install necessary tools and libraries for downloading and extracting files
# RUN apt-get update && apt-get install -y \
#     wget \
#     tar \
#     glpk-utils \
#     z3 \
#     && apt-get clean \
#     && rm -rf /var/lib/apt/lists/*

# # Download the correct MiniZinc bundle
# RUN wget -O MiniZincIDE-latest-bundle-linux-x86_64.tgz https://github.com/MiniZinc/MiniZincIDE/releases/download/2.6.4/MiniZincIDE-2.6.4-bundle-linux-x86_64.tgz

# # Extract the MiniZinc bundle
# RUN tar -xzf MiniZincIDE-latest-bundle-linux-x86_64.tgz --strip-components=1 -C /usr/local \
#     && rm MiniZincIDE-latest-bundle-linux-x86_64.tgz

# # Add MiniZinc to the PATH
# ENV PATH="/usr/local/bin:${PATH}"

# # Install Python dependencies, including the minizinc Python package
# RUN pip3 install minizinc numpy pulp

# # Copy the entire project into the container
# COPY . .

# # Set the entry point for the container to run the main.py script
# ENTRYPOINT ["python3", "main.py"]


# Start with an official Python 3 image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /CDMO

# Install necessary tools and libraries for downloading and extracting files
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

# Download the correct MiniZinc bundle
RUN wget -O MiniZincIDE-latest-bundle-linux-x86_64.tgz https://github.com/MiniZinc/MiniZincIDE/releases/download/2.6.4/MiniZincIDE-2.6.4-bundle-linux-x86_64.tgz

# Extract the MiniZinc bundle
RUN tar -xzf MiniZincIDE-latest-bundle-linux-x86_64.tgz --strip-components=1 -C /usr/local \
    && rm MiniZincIDE-latest-bundle-linux-x86_64.tgz

# Add MiniZinc to the PATH
ENV PATH="/usr/local/bin:${PATH}"

# Install Python dependencies, including the minizinc Python package
RUN pip3 install minizinc numpy pulp

# Copy the entire project into the container
COPY . .

# Set the entry point for the container to run the main.py script
ENTRYPOINT ["python3", "main.py"]
