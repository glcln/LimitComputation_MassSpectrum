#!/bin/bash

#files=("signals_gluino_hybrid_1p4tev.txt")
files=("signals_tauPrime1e.txt")

particle=("#tau'^{1e}")

process=("pp#rightarrow#tau'^{1e}#tau'^{1e}")

mod=("tPrime") 

for i in "${!files[@]}"
do
    #UNBLINDED
    python test_hybrid_limit_tamas.py --signals "${files[i]}" --unblind -p "${particle[i]}" -x "${process[i]}" -m "${mod[i]}" --debug 1

    #BLINDED
    #python test2_limit_tamas.py --signals "${files[i]}" -p "${particle[i]}" -x "${process[i]}" -m "${mod[i]}"
done

