# Preparation
sudo apt update
sudo apt upgrade -y

sudo apt install -y python python-dev python-pip git build-essential cmake libssl-dev

# model repos
mkdir model_repos
cd model_repos

# OpenBLAS
git clone https://github.com/xianyi/OpenBLAS
cd OpenBLAS
make -j8
sudo make install
cd ..

# ML env
sudo pip install -U pip ipython numpy scipy pandas scikit-learn theano future h5py matplotlib seaborn xgboost pydotplus

# CUDA & cuDNN & DIGITS
wget http://developer.download.nvidia.com/compute/cuda/repos/ubuntu1604/x86_64/cuda-repo-ubuntu1604_8.0.61-1_amd64.deb
sudo dpkg -i cuda-repo-ubuntu1604_8.0.61-1_amd64.deb
wget http://developer.download.nvidia.com/compute/machine-learning/repos/ubuntu1604/x86_64/nvidia-machine-learning-repo-ubuntu1604_1.0.0-1_amd64.deb
sudo dpkg -i nvidia-machine-learning-repo-ubuntu1604_1.0.0-1_amd64.deb
sudo apt update
sudo apt install -y cuda libcudnn5 digits 

# disable ECC
sudo nvidia-smi --ecc-config=0

# TensorFlow
sudo pip install tensorflow-gpu

# Keras
git clone https://github.com/fchollet/keras/
cd keras
sudo python setup.py install
cd ..

# Jupyter
sudo pip install -U jupyter jupyter_nbextensions_configurator
sudo jupyter nbextensions_configurator enable --system
git clone https://github.com/ipython-contrib/jupyter_contrib_nbextensions
cd jupyter_contrib_nbextensions
sudo pip install ./
cd ..
sudo jupyter contrib nbextension install --system

# Torch
git clone https://github.com/pytorch/pytorch
cd pytorch
sudo pip install ./
cd ..
