#!/bin/bash

files=("signals_ppStau.txt")

particle=("#tilde{#tau}")

process=("pp#rightarrow#tilde{#tau_{L/R}}#tilde{#tau_{L/R}}")

mod=("tau") 

for i in "${!files[@]}"
do
    #UNBLINDED
    python test_hybrid_limit_tamas.py --signals "${files[i]}" --unblind -p "${particle[i]}" -x "${process[i]}" -m "${mod[i]}"

    #BLINDED
    #python test2_limit_tamas.py --signals "${files[i]}" -p "${particle[i]}" -x "${process[i]}" -m "${mod[i]}"
done

