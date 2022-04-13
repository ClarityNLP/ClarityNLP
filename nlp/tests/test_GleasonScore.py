from custom_tasks.GleasonScoreTask import _find_gleason_score, GleasonScoreResult

SENTENCES = [
        "1. Prostate cancer Gleason 3+2 in two out of 12 cores.",
        "2. Prostate cancer Gleason 3 + 3 in 2 out of twelve cores.",
        "3. Adenocarcinoma, Gleason score 7 (4+3), involving approximately " \
        "5% of the core tissue.",
        "4. The patient is a 62-year old male with a Gleason score 8 " \
        "adenocarcinoma of the prostate involving the left and right lobes.",
        "5. Left lobe, small focus of adenocarcinoma, Gleason's 3 + 3 in " \
        "approximately 5% of the tissue.",
        "6. The patient also had Gleason 6 in the right lobe, midportion, " \
        "well as the left apical portion.",
        "7. The patient also had Gleason's 5 in the right lobe, ",
        "8. Prostate biopsy: Left apex: adenocarcinoma, moderately " \
        "differentiated, Gleason's score 3 + 4 = 7/10.",
        "9. Gleasons score 9 (5+4).",
        "10. Prostate cancer diagnosed with Gleason Score 4+4=8 and 4+5=9.",
        "11. Prostate cancer, Gleason 6 out of 10, diagnosed in...",
        "12. Past Medical History: - Gleason grade 6 (3 + 3) adenocarcinoma.",
        "13. history of prostate cancer, Gleason grade 7-12, s/p TURP.",
        "14. Prostate cancer, Gleason 6 out of 10, diagnosed in ...",
        "15. Adenocarcinoma of prostate with Gleason score of 6 - status",
        "16. ...with surgial pathology revealing a Gleason pattern of 3+4 " \
        "was noted, ...",
        "17. Prostate adenocarcinoma, stage T2c, Gleason score 3+4=7, 6 cores",
        "18. ...diagnosed with prostate cancer with a Gleason score of 8, " \
        "PSA of 38",
        "19. This was a Gleason six adenocarcinoma with negative margins.",
        "20. robot assisted lap prostatectomy -Gleason 4+5  -deferred... ",
        "21. Prostate cancer, T3b N0 M0, Gleason 4+3 stage III  -",
        "22. prostate cancer (Gleason score 7) this past...",
        "23. ...and Gleason Sum 6 adenocarcinoma of the prostate...",
        "24. Prostate ca Dx Jones, intermediate-high grade by Gleason; " \
        "seen by...",
        "25. Prostate CA T3b N0M0 Gleason 4+3 stage III s/p radiation...",
        "26. Prostate cancer: Gleason Grade is 4+3.",
        "27. (Gleason 9+10 prostate cancer recently started on casodex " \
        "will be transitioned to lupron)",
        "28. This was a Gleason six adenocarcinoma with negative margins.",
        "29. Gleason Grade is 4+ He is followed by radiation oncology...",
        "30. His cancer had a Gleason score of 3+.",

        # multiple
        "31. Prostate biopsy which demonstrated with prostate cancer " \
        "demonstrated in 8-29 cores, Gleason 3+3 - [**2532-1-14**] " \
        "prostatectomy was performed with surgical pathology revealing a " \
        "Gleason pattern of 3+4 was noted, one left pelvic lymph node was " \
        "removed, without malignancy identified.",
    ]

EXPECTED = [
    GleasonScoreResult(sentence_index=0, start=19, end=30, score=5, first_num=3, second_num=2),
    GleasonScoreResult(sentence_index=1, start=19, end=32, score=6, first_num=3, second_num=3),
    GleasonScoreResult(sentence_index=2, start=19, end=40, score=7, first_num=4, second_num=3),
    GleasonScoreResult(sentence_index=3, start=44, end=60, score=8, first_num=None, second_num=None),
    GleasonScoreResult(sentence_index=4, start=45, end=60, score=6, first_num=3, second_num=3),
    GleasonScoreResult(sentence_index=5, start=24, end=34, score=6, first_num=None, second_num=None),
    GleasonScoreResult(sentence_index=6, start=24, end=36, score=5, first_num=None, second_num=None),
    GleasonScoreResult(sentence_index=7, start=74, end=95, score=7, first_num=3, second_num=4),
    GleasonScoreResult(sentence_index=8, start=3, end=25, score=9, first_num=5, second_num=4),
    GleasonScoreResult(sentence_index=9, start=35, end=52, score=8, first_num=4, second_num=4),
    GleasonScoreResult(sentence_index=10, start=21, end=31, score=6, first_num=None, second_num=None),
    GleasonScoreResult(sentence_index=11, start=28, end=51, score=6, first_num=3, second_num=3),
    GleasonScoreResult(sentence_index=12, start=32, end=47, score=7, first_num=None, second_num=None),
    GleasonScoreResult(sentence_index=13, start=21, end=31, score=6, first_num=None, second_num=None),
    GleasonScoreResult(sentence_index=14, start=36, end=55, score=6, first_num=None, second_num=None),
    GleasonScoreResult(sentence_index=15, start=42, end=64, score=7, first_num=3, second_num=4),
    GleasonScoreResult(sentence_index=16, start=40, end=57, score=7, first_num=3, second_num=4),
    GleasonScoreResult(sentence_index=17, start=45, end=63, score=8, first_num=None, second_num=None),
    GleasonScoreResult(sentence_index=18, start=15, end=27, score=6, first_num=None, second_num=None),
    GleasonScoreResult(sentence_index=19, start=38, end=49, score=9, first_num=4, second_num=5),
    GleasonScoreResult(sentence_index=20, start=32, end=43, score=7, first_num=4, second_num=3),
    GleasonScoreResult(sentence_index=21, start=21, end=36, score=7, first_num=None, second_num=None),
    GleasonScoreResult(sentence_index=22, start=11, end=25, score=6, first_num=None, second_num=None),
    GleasonScoreResult(sentence_index=23, start=53, end=60, score=None, first_num=None, second_num=None),
    GleasonScoreResult(sentence_index=24, start=25, end=36, score=7, first_num=4, second_num=3),
    GleasonScoreResult(sentence_index=25, start=21, end=41, score=7, first_num=4, second_num=3),
    GleasonScoreResult(sentence_index=26, start=5, end=17, score=9, first_num=None, second_num=None),
    GleasonScoreResult(sentence_index=27, start=15, end=27, score=6, first_num=None, second_num=None),
    GleasonScoreResult(sentence_index=28, start=4, end=22, score=4, first_num=None, second_num=None),
    GleasonScoreResult(sentence_index=29, start=21, end=39, score=3, first_num=None, second_num=None),
    GleasonScoreResult(sentence_index=30, start=88, end=99, score=6, first_num=3, second_num=3),
    GleasonScoreResult(sentence_index=30, start=182, end=204, score=7, first_num=3, second_num=4)
]

def test_find_gleason_score():
    result = _find_gleason_score(SENTENCES)
    assert result == EXPECTED