from custom_tasks.RaceFinderTask import RaceFinderResult, find_race

SENTENCES = [
        '1. The patient is a 42 year old caucasian male.',
        '2. Race: african american woman, 34 years old.',
        '3. African- american female patient.',
        '4. Six month old asian infant in respiratory distress.',
        '5. Native hawaiian gentleman in the ICU.',
        '6. Gender:M, race: white',
        '7. Male patient, age 78 yrs., caucasian, with ...',
        '8. Female, tachycardic, frail pacific islander, BP is ...',
        '9. Child with fractured ulna, 6 y.o. asian, with knee lacerations.',
        '10. Another patient is a 53 year old african american woman.'
    ]

EXPECTED = [
    RaceFinderResult(sentence_index=0, start=32, end=46, race='caucasian', normalized_race='white'),
    RaceFinderResult(sentence_index=0, start=3, end=25, race='african american', normalized_race='black'),
    RaceFinderResult(sentence_index=0, start=3, end=27, race='African- american', normalized_race='black'),
    RaceFinderResult(sentence_index=0, start=17, end=29, race='asian', normalized_race='asian'),
    RaceFinderResult(sentence_index=0, start=3, end=28, race='Native hawaiian', normalized_race='native hawaiian'),
    RaceFinderResult(sentence_index=0, start=13, end=24, race='white', normalized_race='white'),
    RaceFinderResult(sentence_index=0, start=3, end=39, race='caucasian', normalized_race='white'),
    RaceFinderResult(sentence_index=0, start=3, end=46, race='pacific islander', normalized_race='pacific islander'),
    RaceFinderResult(sentence_index=0, start=3, end=42, race='asian', normalized_race='asian'),
    RaceFinderResult(sentence_index=0, start=37, end=59, race='african american', normalized_race='black')
]

def test_find_race():
    for i, s in enumerate(SENTENCES):
        result = find_race([s])
        assert result[0] == EXPECTED[i]