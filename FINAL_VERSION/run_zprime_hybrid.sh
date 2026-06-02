#!/bin/bash

files=("signals_Zprime-M600_ssm.txt")
#files=("signals_Zprime-M800_ssm.txt")

particle=("Z'")

process=("pp#rightarrowZ'#rightarrow#tau'^{#scale[0.5]{ }2e}#tau'^{#scale[0.5]{ }2e}")

mod=("ZPrime") 

for i in "${!files[@]}"
do
    python3 set_limit_noTheory.py --signals "${files[i]}" --unblind -p "${particle[i]}" -x "${process[i]}" -m "${mod[i]}"
    
done

