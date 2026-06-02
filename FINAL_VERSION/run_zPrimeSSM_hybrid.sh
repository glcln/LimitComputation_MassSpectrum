#!/bin/bash

files=("signals_Zprime-M600_ssm.txt")

particle=("Z'_{SSM}")

process=("pp#rightarrowZ'_{SSM}#rightarrow#tau'^{2e}#tau'^{2e}")

mod=("ZPrime") 

for i in "${!files[@]}"
do
    #UNBLINDED
    #python test_hybrid_limit_tamas.py --signals "${files[i]}" --unblind -p "${particle[i]}" -x "${process[i]}" -m "${mod[i]}"

    #BLINDED
    python test_hybrid_limit_tamas.py --signals "${files[i]}" -p "${particle[i]}" -x "${process[i]}" -m "${mod[i]}"
done

