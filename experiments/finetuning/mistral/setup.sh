#!/bin/bash

MODEL_ARCHIVE=mistral-7B-Instruct-v0.3.tar
MODEL_URL=https://models.mistralcdn.com/mistral-7b-v0-3/${MODEL_ARCHIVE}

# move to HOME and clone some repos
cd $HOME \
    && git clone https://github.com/arena-ai/arena.git \
    && git clone https://github.com/mistralai/mistral-finetune.git

# Continue setup
cd ${HOME}/arena/experiments/finetuning/mistral
pip install -r requirements.txt
python3 compute.py data
python3 compute.py config

# Install mistral-finetune
cd ${HOME}/mistral-finetune
pip install -r requirements.txt

mkdir -p ${HOME}/mistral_models
cd ${HOME} && wget -nc ${MODEL_URL}
tar -x --skip-old-files -f ${MODEL_ARCHIVE} -C mistral_models

# python 