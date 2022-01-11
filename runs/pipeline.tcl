# TCL script defining the pipelines for our performance tests.
#
# There is a lot of repetition in the DVC pipelines, some of which is beyond the
# ability of 'foreach' to help with, so we generate the pipelines.
#
# Run this with the following command from the project root directory:
#
#     tclsh runs/pipeline.tcl

source runs/dvcgen.tcl

set excludes [list]

proc key {ds algo} {
    return "$ds-$algo"
}

proc exclude args {
    set ver all
    set ds all
    # reference: https://stackoverflow.com/a/31112023/1385039
    while {[llength $args]} {
        switch -- [lindex $args 0] {
            -v {set args [lassign $args - ver]}
            -d {set args [lassign $args - ds]}
            -* {error "unknown option [lindex $args 0]"}
            default break
        }
    }
    set algo [lindex $args 0]

    lappend ::excludes "$ver/$ds-$algo"
}

proc allowed {ver ds algo} {
    set queries [list "$ver/$ds-$algo" "all/$ds-$algo" "$ver/all-$algo" "all/all-$algo"]
    foreach q $queries {
        if {[expr [lsearch $::excludes $q] >= 0]} {
            return 0
        }
    }
    return 1
}

set versions {
    0.9 0.10 0.11 0.12 0.13
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
