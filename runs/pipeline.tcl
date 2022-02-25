# TCL script defining the pipelines for our performance tests.
#
# There is a lot of repetition in the DVC pipelines, some of which is beyond the
# ability of 'foreach' to help with, so we generate the pipelines.
#
# Run this with the following command from the project root directory:
#
#     tclsh runs/pipeline.tcl

source runs/dvcgen.tcl
source runs/pipe-utils.tcl

set versions {
    0.9 0.10 0.11 0.12 0.13 0.14
    main
}

set datasets {
    ml100k
    ml1m
    ml10m
    ml20m
}

set algorithms {
    II UU ALS IALS
}

exclude -v 0.12 UU
exclude -d ml20m UU

foreach v $versions {
    pipeline "runs/$v/dvc.yaml" {
        set collect_deps [list]
        
        foreach a $algorithms {
            foreach d $datasets {
                if {[allowed $v $d $a]} {
                    stage "$d-$a" {
                        cmd "python envtool.py --run $v run-algo.py --splits data-split/$d -o runs/$v/$d-$a -M runs/$v/$d-$a.json $a"
                        wdir "../.."
                        deps "data-split/$d"
                        outs "runs/$v/$d-$a" "runs/$v/$d-$a.json"
                    }
                    lappend collect_deps "runs/$v/$d-$a.json"
                }
            }
        }

        stage collect {
            cmd "python collect-metrics.py -o runs/$v/metrics.csv runs/$v"
            wdir "../.."
            deps "collect-metrics.py" -l $collect_deps
            outs "runs/$v/metrics.csv"
        }
    }
}
