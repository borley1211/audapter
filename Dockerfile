FROM ubuntu
MAINTAINER borley1211 km.isetan@gmail.com

ENV HOME /root
ENV PYTHON_VERSION 3.8.0
ENV PYENV_ROOT $HOME/.pyenv

RUN apt update && apt upgrade -y
RUN chmod go+w,u+s /tmp

RUN apt install git zsh openssh-server build-essential -y
RUN apt install wget unzip curl tree grep bison libssl-dev openssl zlib1g-dev -y
RUN apt install make bash jq -y

# init Dotfiles
RUN curl -L https://raw.githubusercontent.com/borley1211/dotfiles/master/etc/install | bash
ENV PATH $PYENV_ROOT/shims:$PYENV_ROOT/bin:$PATH

# install Python(pyenv)
RUN echo 'eval "$(pyenv init -)"' >> /etc/profile.d/pyenv.sh && \
    eval "$($PYENV_ROOT/bin/pyenv init -)"
RUN exec "$SHELL"
RUN pyenv update
RUN CFLAGS=-I/usr/include \
    LDFLAGS=-L/usr/lib \
    pyenv install -v $PYTHON_VERSION
RUN pyenv local $PYTHON_VERSION

RUN pip install -U pip setuptools poetry
RUN poetry config settings.virtualenvs.in-directory true
RUN poetry install
