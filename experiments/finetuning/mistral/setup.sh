#!/bin/bash

MODEL_ARCHIVE=mistral-7B-v0.3.tar
MODEL_INSTRUCT_ARCHIVE=mistral-7B-Instruct-v0.3.tar
MODEL_URL=https://models.mistralcdn.com/mistral-7b-v0-3/

# Move to HOME and clone some repos
cd $HOME
# Arena
if [ -d "arena" ]; then
    echo "arena exists"
    (cd arena && git pull)
else
    echo "arena does not exist"
    git clone https://github.com/arena-ai/arena.git
fi
# Finetune
if [ ! -d "mistral-finetune" ]; then
    echo "mistral-finetune does not exists"
    git clone https://github.com/mistralai/mistral-finetune.git
fi
# Inference
if [ ! -d "mistral-inference" ]; then
    echo "mistral-inference does not exists"
    git clone https://github.com/mistralai/mistral-inference.git
fi

# Where the training files are put
mkdir -p ${HOME}/mistral_models

# Setup
cd ${HOME}/arena/experiments/finetuning/mistral
pip install -r requirements.txt
python3 experiment.py data --home ${HOME}
rm ${HOME}/7B_instruct.yaml
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
# export CUDA_VISIBLE_DEVICES="0,1,2,3"
#torchrun -m train ../7B_instruct.yaml

# Install mistral-inference
