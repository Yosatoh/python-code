From ubuntu:latest
Run apt-get update -y && apt-get install -y \
	sudo \
	wget \
	vim
WORKDIR /opt
Run wget https://repo.continuum.io/archive/Anaconda3-2020.11-Linux-x86_64.sh	
CMD ["/bin/bash"]
