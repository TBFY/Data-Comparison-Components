#!/bin/sh
# init.sh

# command: ["./wait-for-it.sh", "db:5432", "--", "python", "app.py"]

set -e

#cd /oesia
#git clone https://github.com/TBFY/Data-Comparison-Components.git
#cd Data-Comparison-Components

# Comprobacion que elascticsearch esta levantado

python /Data-Comparison-Components/script/carga-inicial.py

>&2 echo "Python ejecuted - executing command"
exec $cmd
