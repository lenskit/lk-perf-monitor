local datasets = [
  'ml100k',
  'ml1m',
  'ml10m',
  'ml20m',
];

local algorithms = [
  'II',
  'UU',
  'ALS',
  'IALS',
  'impBPR',
];

local implicit = {
  IALS: true,
  impBPR: true,
};

local forbidden = [
  { a: 'UU', d: 'ml20m' },
];

local default_excludes = [
  { a: 'impBPR' },
];

local rule_matches(rule, obj) =
  local matches = [
    std.get(obj, k.key) == k.value
    for k in std.objectKeysValues(rule)
  ];
  std.all(matches);

local key(d, a) = '%s-%s' % [d, a];

local excluded(excludes, v, d, a) =
  local rules =
    if excludes != null then
      excludes
    else
      default_excludes;
  std.any([
    rule_matches(rule, { v: v, d: d, a: a })
    for rule in rules + forbidden
  ]);

function(version, vtag, excludes=null) {
  stages: {
    [key(d, a)]: {
      cmd: 'pixi run --locked -e %(vt)s run-algo.py --splits data-split/%(d)s%(opts)s -o runs/%(v)s/%(d)s-%(a)s -M runs/%(v)s/%(d)s-%(a)s.json %(a)s' % {
        v: version,
        vt: vtag,
        a: a,
        d: d,
        opts: if std.get(implicit, a, false) then ' --no-predict' else '',
      },
      wdir: '../..',
      deps: [
        'data-split/%s' % [d],
      ],
      outs: [
        'runs/%s/%s' % [version, key(d, a)],
        'runs/%s/%s.json' % [version, key(d, a)],
      ],
    }
    for d in datasets
    for a in algorithms
    if !excluded(excludes, version, d, a)
  } + {
    collect: {
      cmd: 'python collect-metrics.py -o runs/%s/metrics.csv runs/%s' % [version, version],
      wdir: '../..',
      deps: [
        'collect-metrics.py',
      ] + [
        'runs/%s/%s.json' % [version, key(d, a)]
        for d in datasets
        for a in algorithms
        if !excluded(excludes, version, d, a)
      ],
      outs: ['runs/%s/metrics.csv' % [version]],
    },
  },
}
