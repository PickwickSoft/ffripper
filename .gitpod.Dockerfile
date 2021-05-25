FROM gitpod/workspace-full-vnc

# Install custom tools, runtime, etc.
RUN sudo apt-get update \
    && sudo rm -rf /var/lib/apt/lists/* \