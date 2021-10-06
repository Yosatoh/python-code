From ubuntu:latest

# update
Run apt-get update -y && apt-get install -y \
	sudo \
	wget \
	vim \
	build-essential

# install miniconda3
WORKDIR /opt
Run wget https://repo.anaconda.com/miniconda/Miniconda3-py39_4.9.2-Linux-x86_64.sh && \
	sh /opt/Miniconda3-py39_4.9.2-Linux-x86_64.sh -b -p /opt/Miniconda3 && \
	rm -f Miniconda3-py39_4.9.2-Linux-x86_64.sh
# set path
ENV PATH /opt/Miniconda3/bin:$PATH 

# install Library
Run conda install -c conda-forge jupyter jupyterlab && \
	conda install -c conda-forge numpy matplotlib pandas && \
	conda install -c conda-forge scipy seaborn && \
    conda install -c conda-forge scikit-learn statsmodels

WORKDIR /
# CMD ["bash"]
CMD ["jupyter", "lab", "--ip=0.0.0.0", "--allow-root", "--LabApp.token=''"]
# docker run -p 8888:8888 -v ~/Desktop/python/for_volume:/work --name py39 ID

