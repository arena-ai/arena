#!/bin/bash

MODEL_ARCHIVE=mistral-7B-v0.3.tar
MODEL_INSTRUCT_ARCHIVE=mistral-7B-Instruct-v0.3.tar
MODEL_URL=https://models.mistralcdn.com/mistral-7b-v0-3/

# move to HOME and clone some repos
cd $HOME \
    && git clone https://github.com/arena-ai/arena.git \
    && git clone https://github.com/mistralai/mistral-finetune.git

# Where the training files are put
mkdir -p ${HOME}/mistral_models

# Setup
cd ${HOME}/arena/experiments/finetuning/mistral
pip install -r requirements.txt
python3 experiment.py data --home ${HOME}
python3 experiment.py config --home ${HOME}

# Download the models
cd ${HOME}
wget -nc ${MODEL_URL}${MODEL_ARCHIVE}
mkdir -p ${HOME}/mistral_models/7B
tar -x --skip-old-files -f ${MODEL_ARCHIVE} -C mistral_models/7B
wget -nc ${MODEL_URL}${MODEL_INSTRUCT_ARCHIVE}
mkdir -p ${HOME}/mistral_models/7B_instruct
tar -x --skip-old-files -f ${MODEL_INSTRUCT_ARCHIVE} -C mistral_models/7B_instruct

# Install mistral-finetune
cd ${HOME}/mistral-finetune
pip install -r requirements.txt
# Run the training
export CUDA_VISIBLE_DEVICES=0
# torchrun --nproc-per-node 1 --master_port $RANDOM -m train ../7B_instruct.yaml