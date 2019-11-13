FROM ubuntu
MAINTAINER borley1211 km.isetan@gmail.com

ENV HOME /root
ENV PYTHON_VERSION 3.8.0
ENV PYENV_ROOT $HOME/.pyenv

RUN apt-get update && apt-get upgrade -y && apt-get install apt-utils -y
RUN chmod go+w,u+s /tmp

RUN apt-get install git zsh openssh-server build-essential -y
RUN apt-get install wget unzip curl tree grep bison libssl-dev openssl zlib1g-dev -y
RUN apt-get install make bash jq -y

# init Dotfiles
RUN curl -L https://raw.githubusercontent.com/borley1211/dotfiles/master/etc/install | bash
WORKDIR $HOME/Dotfiles
RUN make init
WORKDIR $HOME
ENV PATH $PYENV_ROOT/bin:$PYENV_ROOT/shims:$PATH

# install Python(pyenv)
RUN mkdir -p /etc/profile.d
RUN echo 'eval "$(pyenv init -)"' >> /etc/profile.d/pyenv.sh
RUN eval "$(pyenv init -)"
RUN pyenv update
RUN CFLAGS=-I/usr/include \
    LDFLAGS=-L/usr/lib \
    pyenv install -v $PYTHON_VERSION
RUN pyenv local $PYTHON_VERSION

RUN pip install -U pip setuptools poetry
RUN poetry config settings.virtualenvs.in-directory true
RUN poetry install
