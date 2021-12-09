# TCL script defining the pipelines for our performance tests.
#
# There is a lot of repetition in the DVC pipelines, some of which is beyond the
# ability of 'foreach' to help with, so we generate the pipelines.

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
    set fp [open "runs/$v/dvc.yaml" w]
    set outs [list]
    puts $fp "stages:"
    foreach a $algorithms {
        foreach d $datasets {
            if {[allowed $v $d $a]} {
                puts "writing $v: $d-$a"
                lappend outs "$d-$a"
                puts $fp "  $d-$a:"
                puts $fp "    cmd: python envtool.py --run run-algo.py --splits data-split/$d -o runs/$v/$d-$a -M runs/$v/$d-$a.json $a"
                puts $fp "    wdir: ../.."
                puts $fp "    deps:"
                puts $fp "    - data-split/$d"
                puts $fp "    outs:"
                puts $fp "    - runs/$v/$d-$a"
                puts $fp "    - runs/$v/$d-$a.json"
            }
        }
    }

    puts $fp "  collect:"
    puts $fp "    cmd: python collect-metrics.py -o runs/$v/metrics.csv runs/$v"
    puts $fp "    wdir: ../.."
    puts $fp "    deps:"
    foreach dep $outs {
        puts $fp "    - runs/$v/$dep.json"
    }
    puts $fp "    outs:"
    puts $fp "    - runs/$v/metrics.csv"

    close $fp
}
