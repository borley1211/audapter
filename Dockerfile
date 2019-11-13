FROM ubuntu

ENV HOME /root
ENV PYTHON_VERSION 3.8.0
ENV PYENV_ROOT $HOME/.pyenv

RUN apt-get update && apt-get upgrade -y && apt-get install apt-utils -y
RUN chmod go+w,u+s /tmp

RUN apt-get install git zsh openssh-server build-essential bash -y
RUN apt-get install wget unzip curl tree grep bison openssl -y
RUN apt-get install make libssl-dev zlib1g-dev libbz2-dev libreadline-dev \
    libsqlite3-dev wget curl llvm libncurses5-dev xz-utils tk-dev libxml2-dev \
    libxmlsec1-dev libffi-dev liblzma-dev -y

# init Dotfiles
RUN curl -L https://raw.githubusercontent.com/borley1211/dotfiles/master/etc/install | bash
WORKDIR $HOME/Dotfiles
RUN make init
WORKDIR $HOME
ENV PATH $PYENV_ROOT/bin:$PYENV_ROOT/shims:$PATH

# install Python(pyenv)
RUN mkdir -p /etc/profile.d
RUN echo 'eval "$(pyenv init -)"' >> /etc/profile.d/pyenv.sh
RUN echo 'eval "$(pyenv virtualenv-init -)"' >> /etc/profile.d/pyenv-virtualenv.sh
RUN eval "$(pyenv init -)" && eval "$(pyenv virtualenv-init -)"
RUN CFLAGS=-I/usr/include \
    LDFLAGS=-L/usr/lib \
    pyenv install $PYTHON_VERSION
RUN pyenv global $PYTHON_VERSION
RUN pyenv local $PYTHON_VERSION

RUN pip install -U pip setuptools
RUN pip install poetry
RUN poetry config settings.virtualenvs.in-directory true
RUN poetry install
