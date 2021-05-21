From ubuntu:latest

# update
Run apt-get update -y && apt-get install -y \
	sudo \
	wget \
	vim

# install miniconda3
WORKDIR /opt
Run wget https://repo.anaconda.com/miniconda/Miniconda3-py37_4.8.2-Linux-x86_64.sh && \
	sh /opt/Miniconda3-py37_4.8.2-Linux-x86_64.sh -b -p /opt/Miniconda3 && \
	rm -f Miniconda3-py37_4.8.2-Linux-x86_64.sh
# set path
ENV PATH /opt/Miniconda3/bin:$PATH 

# install Library
Run conda install -c conda-forge jupyter jupyterlab 
Run conda install -c conda-forge numpy==1.15.4 matplotlib==3.02 pandas==0.23.4 \
	scipy==1.1.0 seaborn==0.9.0 pymc3==3.6 theano==1.04

CMD ["/bin/bash"]

