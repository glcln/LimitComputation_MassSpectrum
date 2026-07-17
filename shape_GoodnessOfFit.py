from optparse import OptionParser
import os
import sys
import shutil
import json

if __name__ == '__main__':

    parser = OptionParser()
    parser.add_option('--splitEta', action='store_true', dest='splitEta', default=False)
    parser.add_option('--onlyEta1', action='store_true', dest='onlyEta1', default=False)
    parser.add_option('--algo', type='string', default='saturated', dest='algo')
    parser.add_option('--toys', type='int', default=500, dest='toys')
    parser.add_option('--seed', type='int', default=123456, dest='seed')
    parser.add_option('--toysFreq', action='store_true', default=False, dest='toysFreq')
    parser.add_option('--fixedSignalStrength', type='string', default='', dest='fixedR')
    parser.add_option('--sample', type='string', default='', dest='sample')
    parser.add_option('--extraOpts', type='string', default='', dest='extraOpts')
    parser.add_option('--dryRun', action='store_true', default=False, dest='dryRun')
    parser.add_option('-d', '--debug', type='int', default=1, dest='debug')
    (options, args) = parser.parse_args()

    splitEta = options.splitEta
    onlyEta1 = options.onlyEta1
    debug    = options.debug
    dryRun   = options.dryRun

    algo = options.algo
    toysFreq = options.toysFreq or (algo == 'saturated')

    regionBckg = '9fp10'
    tag = 'etaRebinPerso_Oldfit__PUppiMETcut'

    if splitEta:
        etaLabel = 'split_Eta1_Eta1_2p4'
    elif onlyEta1:
        etaLabel = 'Eta1'
    else:
        etaLabel = 'Eta2p4'

    idir = 'MyNewDataCards/datacards_shape_{}_{}_{}'.format(regionBckg, etaLabel, tag)
    odir = 'MyNewDataCards/gof_shape_{}_{}_{}_{}'.format(regionBckg, etaLabel, algo, tag)
    os.makedirs(odir, exist_ok=True)

    idir_abs = os.path.abspath(idir)
    odir_abs = os.path.abspath(odir)
    launch_dir = os.getcwd()

    print("Datacards : {}".format(idir_abs))
    print("Sorties   : {}".format(odir_abs))
    print("Algo : {} | toys : {} | toysFrequentist : {} | r : {}".format(
        algo, options.toys, toysFreq, options.fixedR if options.fixedR else 'flottant'))

    all_samples = [
        'Gluino1100_2024', 'Gluino1200_2024', 'Gluino1300_2024', 'Gluino1400_2024',
        'Gluino1600_2024', 'Gluino1800_2024', 'Gluino2000_2024', 'Gluino2200_2024',
        'Gluino2400_2024', 'Gluino2600_2024',
    ]
    all_samples = ['Gluino2000_2024']

    if options.sample:
        if options.sample not in all_samples:
            sys.exit("Sample inconnu : {} (attendus : {})".format(options.sample, all_samples))
        samples = [options.sample]
    else:
        samples = all_samples

    def build_commands(name, mass):
        datacard = os.path.join(idir_abs, name + '.txt')
        workdir  = os.path.join(odir_abs, name)

        freq  = ' --toysFrequentist' if toysFreq else ''
        fixR  = (' --fixedSignalStrength ' + options.fixedR) if options.fixedR else ''
        extra = (' ' + options.extraOpts) if options.extraOpts else ''
        common = '-M GoodnessOfFit -d {dc} -m {m} --algo {a}'.format(dc=datacard, m=mass, a=algo)

        n_data = '.{}_data'.format(name)
        n_toys = '.{}_toys'.format(name)
        f_data = 'higgsCombine{}.GoodnessOfFit.mH{}.root'.format(n_data, mass)
        f_toys = 'higgsCombine{}.GoodnessOfFit.mH{}.{}.root'.format(n_toys, mass, options.seed)

        jsonOut = '{}_gof.json'.format(name)

        cmds = [
            ('combine {c} -n {n}{fx}{ex}'.format(
                c=common, n=n_data, fx=fixR, ex=extra), launch_dir),
            ('combine {c} -n {n} -t {t} -s {s}{fq}{fx}{ex}'.format(
                c=common, n=n_toys, t=options.toys, s=options.seed, fq=freq, fx=fixR, ex=extra), launch_dir),
            ('combineTool.py -M CollectGoodnessOfFit --input {fd} {ft} -o {j}'.format(
                fd=f_data, ft=f_toys, j=jsonOut), launch_dir),
        ]

        outputs = {'f_data': f_data, 'f_toys': f_toys, 'json': jsonOut}
        return datacard, workdir, outputs, cmds

    def run(cmd, cwd):
        full = 'cd {} && {}'.format(cwd, cmd)
        if debug > 0 or dryRun:
            print('  ' + full)
        if not dryRun:
            rc = os.system(full)
            if rc != 0:
                print('  -> ECHEC (code {}) : {}'.format(rc, cmd))
                return False
        return True

    def print_pvalue(json_path):
        d = json.load(open(json_path))
        key = list(d.keys())[0]
        node = d[key]
        obs = node['obs'][0] if isinstance(node['obs'], list) else node['obs']
        toys = node['toy']
        n_ge = sum(1 for t in toys if t >= obs)
        p = n_ge / float(len(toys))
        print("  obs (t_data) : {:.4f}".format(obs))
        print("  n toys       : {}".format(len(toys)))
        print("  p-value      : {:.4f}".format(p))

    for name in samples:
        print('\n=== {} ==='.format(name))
        mass = name.split('_')[0].replace('Gluino', '')
        datacard, workdir, outputs, cmds = build_commands(name, mass)

        if not os.path.isfile(datacard) and not dryRun:
            print('WARNING: datacard manquante, on saute : {}'.format(datacard))
            continue

        os.makedirs(workdir, exist_ok=True)

        ok = True
        for cmd, cwd in cmds:
            ok = run(cmd, cwd)
            if not ok:
                print('  Arret de la sequence pour {}.'.format(name))
                break

        if ok and not dryRun:
            for key in ('f_data', 'f_toys', 'json'):
                src = os.path.join(launch_dir, outputs[key])
                if os.path.isfile(src):
                    shutil.move(src, os.path.join(workdir, outputs[key]))
            json_final = os.path.join(workdir, outputs['json'])
            if os.path.isfile(json_final):
                print_pvalue(json_final)
            else:
                print('  WARNING: JSON introuvable : {}'.format(json_final))

    print('\nTermine.')