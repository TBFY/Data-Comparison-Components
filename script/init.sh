#!/bin/sh
# init.sh

mkdir /oesia
cd /oesia
git clone https://github.com/TBFY/Data-Comparison-Components.git
cd Data-Comparison-Components

# Comprobacion que elascticsearch esta levantado

python /oesia/Data-Comparison-Components/script/carga-inicial.py
