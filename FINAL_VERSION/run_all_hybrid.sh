#!/bin/bash

#files=("signals_gluino_v1.txt" "signals_stop.txt" "signals_tauPrime2e.txt" "signals_tauPrime1e.txt" "signals_ppStau.txt" "signals_ppStauL.txt" "signals_ppStauR.txt" "signals_Zprime-M600.txt"  "signals_Zprime-M600_ssm.txt" "signals_ppStauGMSB.txt")
#particle=("#tilde{g}" "#tilde{t}" "#tau'^{#scale[0.5]{ }2e}" "#tau'^{#scale[0.5]{ }1e}" "#tilde{#tau}" "#tilde{#tau}" "#tilde{#tau}" "Z'_{#psi}" "Z'_{SSM}" "#tilde{#tau}")
#process=("pp#rightarrow#tilde{g}#tilde{g}" "pp#rightarrow#tilde{t}#tilde{t}" "pp#rightarrow#tau'^{#scale[0.5]{ }2e}#tau'^{#scale[0.5]{ }2e}" "pp#rightarrow#tau'^{#scale[0.5]{ }1e}#tau'^{#scale[0.5]{ }1e}" "pp#rightarrow#tilde{#tau}#tilde{#tau}" "pp#rightarrow#tilde{#tau}#tilde{#tau}(L)" "pp#rightarrow#tilde{#tau}#tilde{#tau}(R)" "pp#rightarrowZ'_{#psi}#rightarrow#tau'^{#scale[0.5]{ }2e}#tau'^{#scale[0.5]{ }2e}" "pp#rightarrowZ'_{SSM}#rightarrow#tau'^{#scale[0.5]{ }2e}#tau'^{#scale[0.5]{ }2e}" "pp#rightarrow#tilde{#tau}#tilde{#tau}(GMSB)")
#mod=("gluino" "stop" "tPrime" "tPrime" "tau" "tau" "tau" "ZPrime" "ZPrime" "tau") 

files=("signals_ppStau.txt")
particle=("#tilde{#tau}")
process=("pp#rightarrow#tilde{#tau}#tilde{#tau}")
mod=("tau") 

for i in "${!files[@]}"
do
    #UNBLINDED
    python test_hybrid_limit_tamas.py --signals "${files[i]}" --unblind -p "${particle[i]}" -x "${process[i]}" -m "${mod[i]}"
    if [ "${files[i]}" = "signals_Zprime-M600_ssm.txt" ]; then
        python3 set_limit_noTheory_hybrid_ionisation.py --signals "${files[i]}" --unblind -p "${particle[i]}" -x "${process[i]}" -m "${mod[i]}"
    fi
    #BLINDED
    #python test2_limit_tamas.py --signals "${files[i]}" -p "${particle[i]}" -x "${process[i]}" -m "${mod[i]}"
done