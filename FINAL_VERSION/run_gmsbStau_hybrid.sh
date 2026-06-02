#!/bin/bash

files=("signals_ppStauGMSB.txt")

particle=("#tilde{#tau}")

process=("pp#rightarrow#tilde{#tau}#tilde{#tau}(GMSB)")

mod=("tau") 

for i in "${!files[@]}"
do
    #UNBLINDED
    python test_hybrid_limit_tamas.py --signals "${files[i]}" --unblind -p "${particle[i]}" -x "${process[i]}" -m "${mod[i]}"

    #BLINDED 
    #python test_hybrid_limit_tamas.py --signals "${files[i]}" -p "${particle[i]}" -x "${process[i]}" -m "${mod[i]}"
done

