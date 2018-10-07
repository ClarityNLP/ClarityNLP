import numpy as np


def get_exclusion_criteria_index(criteria):
    try:
        ex_index = criteria.lower().index("exclusion criteria")
    except ValueError:
        ex_index = -1
    return ex_index


def read_aact():
    # Sample AACT data read from here - https://www.ctti-clinicaltrials.org/aact-database
    with open('data/clinical_study.txt') as f:
        cols = None
        results = list()

        txt = ''
        for i, line in enumerate(f):

            if i == 0:
                cols = line.split('|')
            else:
                if line.startswith('NCT') and len(txt) > 0:
                    res = txt.split('|')
                    criteria = res[26]

                    ex_index = get_exclusion_criteria_index(criteria)

                    if ex_index >= 0:
                        inclusion = criteria[0:ex_index]
                        exclusion = criteria[ex_index:]
                    else:
                        inclusion = criteria
                        exclusion = ''
                    new_row = [res[0], inclusion, exclusion, res[27], res[28], res[29]]
                    if criteria != 'Please contact site for information.':
                        results.append(new_row)
                    txt = line
                else:
                    if len(line.strip()) > 0:
                        txt = txt + line

        print(len(results))
        return results


if __name__ == "__main__":
    read_aact()
