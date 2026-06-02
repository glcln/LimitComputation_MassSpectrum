#!/bin/bash

#files=("signals_gluino_hybrid_1p4tev.txt")
files=("signals_tauPrime2e.txt")

particle=("#tau'^{2e}")

process=("pp#rightarrow#tau'^{2e}#tau'^{2e}")

mod=("tPrime") 

for i in "${!files[@]}"
do
    #UNBLINDED
    python test_hybrid_limit_tamas.py --signals "${files[i]}" --unblind -p "${particle[i]}" -x "${process[i]}" -m "${mod[i]}" --debug 1

    #BLINDED
    #python test2_limit_tamas.py --signals "${files[i]}" -p "${particle[i]}" -x "${process[i]}" -m "${mod[i]}"
done

