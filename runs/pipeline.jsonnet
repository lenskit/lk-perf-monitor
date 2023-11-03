local datasets = [
    "ml100k",
    "ml1m",
    "ml10m",
    "ml20m",
];

local algorithms = [
    "II",
    "UU",
    "ALS",
    "IALS",
];

local default_excludes = [
    {a: "UU", d: "ml20m"},
    {a: "implicit"}
];

local rule_matches(rule, obj) =
    local matches = [
        std.get(obj, k.key) == k.value
        for k in std.objectKeysValues(rule)
    ];
    std.all(matches);

local key(d, a) = "%s-%s" % [d, a];

local excluded(excludes, v, d, a) =
    local rules =
        if std.length(excludes) > 0 then
            excludes
        else
            default_excludes;
    std.any([
        rule_matches(rule, {v: v, d: d, a: a})
        for rule in excludes + default_excludes
    ]);

function(version, excludes=[]) {
    stages: {
        [key(d, a)]: {
            cmd: "python envtool.py --run %(v)s run-algo.py --splits data-split/%(d)s -o runs/%(v)s/%(d)s-%(a)s -M runs/%(v)s/%(d)s-%(a)s.json %(a)s" % {
                v: version,
                a: a,
                d: d,
            },
            wdir: "../..",
            deps: [
                "data-split/%s" % [d]
            ],
            outs: [
                "runs/%s/%s" % [version, key(d, a)],
                "runs/%s/%s.json" % [version, key(d, a)],
            ]
        }
        for d in datasets
        for a in algorithms
        if !excluded(excludes, version, d, a)
    } + {
        collect: {
            cmd: "python collect-metrics.py -o runs/%s/metrics.csv runs/%s" % [version, version],
            wdir: "../..",
            deps: [
                "collect-metrics.py"
            ] + [
                "runs/%s/%s.json" % [version, key(d, a)]
                for d in datasets
                for a in algorithms
                if !excluded(excludes, version, d, a)
            ],
            outs: ["runs/%s/metrics.csv" % [version]]
        }
    },
}
