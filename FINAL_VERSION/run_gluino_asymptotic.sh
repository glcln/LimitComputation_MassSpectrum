#!/bin/bash

files=("signals_gluino_hybrid_1p4tev.txt")

particle=("#tilde{g}")

process=("pp#rightarrow#tilde{g}#tilde{g}")

mod=("gluino") 

for i in "${!files[@]}"
do
    #UNBLINDED
    python test2_limit_tamas.py --signals "${files[i]}" --unblind -p "${particle[i]}" -x "${process[i]}" -m "${mod[i]}" --debug 1

    #BLINDED
    #python test2_limit_tamas.py --signals "${files[i]}" -p "${particle[i]}" -x "${process[i]}" -m "${mod[i]}"
done

