from custom_tasks.EcogCriteriaTask import EcogResult, _find_ecog_scores

SENTENCES = [
        # single
        "ECOG status                                                  4",
        "Eastern Cooperative Oncology Group (ECOG) Performance Status 2",
        "Eastern Cooperative Oncology Group(ECOG) score standard      1",
        
        # inequalities
        "Eastern Cooperative Oncology Group (ECOG) > 1",
        "Eastern Cooperative Oncology Group (ECOG) <=2",
        "ECOG performance status >2",
        "Eastern Cooperative Oncology Group (ECOG) Performance Status < 1",
        "Eastern Cooperative Oncology Group (ECOG) performance status (PS) > 3",
        "Eastern Cooperative Oncology Group (ECOG) performance status of equal to or less than 3",
        "Eastern Cooperative Oncology Group (ECOG) performance status < or = 2",
        "Eastern Cooperative Oncology Group (ECOG) performance status </= 2",
        "Eastern Cooperative Oncology Group (ECOG) Performance Status of < 2",
        "ECOG(Eastern cooperative Oncology Group) performance status <=3",
        "ECOG [Eastern Cooperative Oncology Group] </=1",
        "The Eastern Cooperative Oncology Group (ECOG) score < 4",

        # range lo-hi
        "Eastern Cooperative Oncology Group (ECOG)                         0 or 1",
        "Eastern Cooperative Oncology Group (ECOG)                         0 -  2",
        "Eastern Cooperative Oncology Group                                0 -  1",
        "Eastern Cooperative Oncology Group (ECOG) PS of                   0 or 1",
        "Eastern Cooperative Oncology Group Performance (ECOG) status      0 -  3",
        "Eastern Cooperative Oncology Group (ECOG) performance status      0 or 1",
        "Eastern Cooperative Oncology Group (ECOG)              grade      0 or 1",
        "Eastern Cooperative Oncology Group (ECOG) performance status of   0 or 1",
        "Eastern Cooperative Oncology Group (ECOG) status of               0 to 2",
        "Eastern Cooperative Oncology Group (ECOG) performance score of    0 or 1",
        "Eastern Cooperative Oncology Group (ECOG) Performance Status =    0 -  1",
        "Eastern Cooperative Oncology Group (ECOG) Performance Status (PS) 0 or 1",
        "Eastern Cooperative Oncology Group (ECOG) performance status of   0, or 1",
        
        # triples
        "Eastern Cooperative Oncology Group (ECOG) performance status 0, 1, or 2",
        "ECOG (Eastern Cooperative Oncology Group) performance status of 0,1,or 2",
        "Eastern Cooperative Oncology Group (ECOG) performance status of 2, 3 or 4",

        # quads
        "ECOG (Eastern Cooperative Oncology Group) performance status of 0, 1, 2 or 3",
    ]

EXPECTED = [
    [EcogResult(sentence='ECOG status                                                  4', start=0, end=62, inc_or_ex=1, score_min=4, score_max=None)],
    [],
    [],
    [],
    [],
    [EcogResult(sentence='ECOG performance status >2', start=0, end=26, inc_or_ex=1, score_min=3, score_max=5)],
    [],
    [],
    [],
    [],
    [],
    [],
    [],
    [],
    [],
    [],
    [],
    [EcogResult(sentence='Eastern Cooperative Oncology Group                                0 -  1', start=0, end=72, inc_or_ex=1, score_min=0, score_max=1)],
    [],
    [],
    [],
    [],
    [],
    [],
    [],
    [],
    [],
    [],
    [],
    [],
    [],
    []
]

def test_ecog():
    result = [_find_ecog_scores(x) for x in SENTENCES]
    assert EXPECTED == result