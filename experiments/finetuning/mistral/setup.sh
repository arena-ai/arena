#!/bin/bash

MODEL_ARCHIVE=mistral-7B-Instruct-v0.3.tar
MODEL_URL=https://models.mistralcdn.com/mistral-7b-v0-3/${MODEL_ARCHIVE}

# move to HOME and clone some repos
cd $HOME \
    && git clone https://github.com/arena-ai/arena.git \
    && git clone https://github.com/mistralai/mistral-finetune.git
# 
cd mistral-finetune
pip install -r requirements.txt

mkdir -p ${HOME}/mistral_models
cd ${HOME} && wget ${MODEL_URL}
tar -xf ${MODEL_ARCHIVE} -C mistral_models