# Helper routines for defining a DVC pipeline.

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
