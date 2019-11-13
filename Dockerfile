FROM Ubuntu:18.04
MAINTAINER borley1211 km.isetan@gmail.com

ENV PYTHON_VERSION 3.8.0
ENV PYENV_ROOT $HOME/.pyenv
ENV PATH $PYENV_ROOT/shims:$PYENV_ROOT/bin:$PATH

RUN apt update && apt upgrade -y
RUN chmod go+w,u+s /tmp

RUN apt install git zsh openssh-server build-essential -y
RUN apt install wget unzip curl tree grep bison libssl-dev openssl zlib1g-dev -y
RUN apt install make bash jq -y

# init Dotfiles
RUN curl -L https://raw.githubusercontent.com/borley1211/dotfiles/master/etc/install | bash

RUN sed -i 's/.*session.*required.*pam_loginuid.so.*/session optional pam_loginuid.so/g' /etc/pam.d/sshd
RUN mkdir -p /var/run/sshd

# install Python(pyenv)
RUN exec $(pyenv init -)
RUN pyenv update
RUN pyenv install $PYTHON_VERSION
RUN pyenv local $PYTHON_VERSION

RUN pip install -U pip setuptools poetry
RUN poetry config settings.virtualenvs.in-directory true
RUN poetry install
