From ubuntu:latest

# update
Run apt-get update -y && apt-get install -y \
	sudo \
	wget \
	vim

# install anaconda3
WORKDIR /opt
Run wget https://repo.continuum.io/archive/Anaconda3-2020.11-Linux-x86_64.sh && \
	sh /opt/Anaconda3-2020.11-Linux-x86_64.sh -b -p /opt/anaconda3 && \
	rm -f Anaconda3-2020.11-Linux-x86_64.sh
# set path
ENV PATH /opt/anaconda3/bin:$PATH

# update pip
Run pip install --upgrade pip

CMD ["/bin/bash"]
