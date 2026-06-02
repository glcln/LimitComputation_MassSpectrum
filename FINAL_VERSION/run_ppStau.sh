#!/bin/bash

files=("signals_ppStau.txt" "signals_ppStauL.txt" "signals_ppStauR.txt")

particle=("#tilde{#tau}" "#tilde{#tau}" "#tilde{#tau}")

process=("pp#rightarrow#tilde{#tau_{L/R}}#tilde{#tau_{L/R}}" "pp#rightarrow#tilde{#tau_{L}}#tilde{#tau_{L}}" "pp#rightarrow#tilde{#tau_{R}}#tilde{#tau_{R}}")

mod=("tau" "tau" "tau") 

for i in "${!files[@]}"
do
    #UNBLINDED
    python test2_limit_tamas.py --signals "${files[i]}" --unblind -p "${particle[i]}" -x "${process[i]}" -m "${mod[i]}"

    #BLINDED
    #python test2_limit_tamas.py --signals "${files[i]}" -p "${particle[i]}" -x "${process[i]}" -m "${mod[i]}"
done

