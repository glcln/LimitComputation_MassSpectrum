#!/bin/bash

files=("signals_tauPrime2e_ionization_asymp.txt")

particle=("#tau'^{#scale[0.5]{ }2e}")

process=("pp#rightarrow#tau'^{#scale[0.5]{ }2e}#tau'^{#scale[0.5]{ }2e}")

mod=("tPrime") 

for i in "${!files[@]}"
do
    #UNBLINDED
    python test2_limit_tamas_ionization.py --signals "${files[i]}" --unblind -p "${particle[i]}" -x "${process[i]}" -m "${mod[i]}" --debug 1

done

