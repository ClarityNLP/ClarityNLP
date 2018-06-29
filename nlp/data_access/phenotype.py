import psycopg2
import psycopg2.extras

try:
    from .base_model import BaseModel
    from .pipeline_config import PipelineConfig
except Exception as e:
    print(e)
    from base_model import BaseModel
    from pipeline_config import PipelineConfig


class PhenotypeDefine(dict):

    def __init__(self, name: str, declaration: str, alias: str = '', version: str = '', library: str = 'ClarityNLP',
                 named_arguments: dict = dict(),
                 arguments: list = list(), funct: str = '', values: list = list(), description: str = '',
                 concept: str = ''):
        dict.__init__(self, name=name, declaration=declaration, version=version, alias=alias, arguments=arguments,
                      named_arguments=named_arguments, library=library, funct=funct, values=values,
                      description=description, concept=concept)


class PhenotypeEntity(dict):

    def __init__(self, name: str, declaration: str, alias: str = '', version: str = '', library: str = '',
                 named_arguments: dict = dict(),
                 arguments: list = list(), funct: str = '', values: list = list(), description: str = '',
                 concept: str = '', final: bool = False, raw_text: str = ''):
        dict.__init__(self, name=name, declaration=declaration, version=version, alias=alias, arguments=arguments,
                      named_arguments=named_arguments, library=library, funct=funct, values=values,
                      description=description, concept=concept, final=final, raw_text=raw_text)


class PhenotypeOperations(dict):

    def __init__(self, name: str, action: str, data_entities: list, final: bool = False, raw_text: str = ''):
        dict.__init__(self, name=name, action=action, data_entities=data_entities, final=final, raw_text=raw_text)


class PhenotypeModel(BaseModel):

    # data_models maps to 'using'
    def __init__(self, description: str = '', owner: str = 'clarity', context: str = 'Patient', population: str = 'All',
                 phenotype=None, data_models: list = list(),
                 includes: list = list(), code_systems: list = list(),
                 value_sets: list = list(), term_sets: list = list(),
                 document_sets: list = list(), data_entities: list = list(), cohorts: list = list(),
                 operations: list = list(), debug=False, limit: int = 0):
        self.owner = owner
        self.description = description
        self.population = population
        self.context = context
        self.data_models = data_models
        self.phenotype = phenotype
        self.includes = includes
        self.code_systems = code_systems
        self.value_sets = value_sets
        self.term_sets = term_sets
        self.document_sets = document_sets
        self.data_entities = data_entities
        self.cohorts = cohorts
        self.operations = operations
        self.debug = debug
        self.limit = limit


def insert_phenotype_mapping(phenotype_id, pipeline_id, connection_string):
    conn = psycopg2.connect(connection_string)
    cursor = conn.cursor()

    try:
        cursor.execute("""
                     INSERT INTO nlp.phenotype_mapping(phenotype_id, pipeline_id) VALUES
                     (%s, %s) 
                      """, (phenotype_id, pipeline_id))

        conn.commit()

    except Exception as ex:
        print('failed to insert phenotype mapping')
        print(str(ex))
    finally:
        conn.close()

    return 'done'


def insert_phenotype_model(phenotype: PhenotypeModel, connection_string: str):
    conn = psycopg2.connect(connection_string)
    cursor = conn.cursor()
    p_id = -1

    try:
        if len(phenotype.description) > 250:
            name = phenotype.description[0:249]
        else:
            name = phenotype.description
        p_json = phenotype.to_json()
        cursor.execute("""
                      INSERT INTO nlp.phenotype(owner, config, name, description, date_created) 
                      VALUES(%s, %s, %s, %s, current_timestamp) RETURNING phenotype_id
                      """, (phenotype.owner, p_json, name, phenotype.description))

        p_id = cursor.fetchone()[0]
        conn.commit()

    except Exception as ex:
        print('failed to insert phenotype')
        print(str(ex))
    finally:
        conn.close()

    return p_id


def query_pipeline_ids(phenotype_id: int, connection_string: str):
    conn = psycopg2.connect(connection_string)
    cursor = conn.cursor()
    pipeline_ids = list()

    try:

        cursor.execute("""SELECT pipeline_id FROM nlp.phenotype_mapping WHERE phenotype_id = %s""",
                       [phenotype_id])
        rows = cursor.fetchall()
        for row in rows:
            pipeline_ids.append(row[0])

        return pipeline_ids
    except Exception as ex:
        print(ex)
    finally:
        conn.close()

    return pipeline_ids


def query_phenotype(phenotype_id: int, connection_string: str):
    conn = psycopg2.connect(connection_string)
    cursor = conn.cursor()
    phenotype = None

    try:

        cursor.execute("""SELECT config FROM nlp.phenotype WHERE phenotype_id = %s""",
                       [phenotype_id])
        val = cursor.fetchone()[0]
        phenotype = PhenotypeModel.from_json(val)

        return phenotype
    except Exception as ex:
        print(ex)
    finally:
        conn.close()

    return phenotype


def get_sample_phenotype():
    ptype = PhenotypeDefine('Sepsis', 'phenotype', version='1')
    using_omop = PhenotypeDefine('OMOP', 'datamodel', version='5.3')
    clarity_core = PhenotypeDefine('ClarityCore', 'include', version='1.0', alias='ClarityNLP')
    ohdsi_helpers = PhenotypeDefine('OHDSIHelpers', 'include', version='1.0', alias='OHDSI')
    omop = PhenotypeDefine('OMOP', 'codesystem', values=['http://omop.org'])
    isbt = PhenotypeDefine('ISBT', 'codesystem', values=['https://www.iccbba.org'])
    # Sepsis = PhenotypeDefine('Sepsis', 'valueset', library='OHDSI',
    #                          funct='getConceptSet',
    #                          arguments=['assets/Sepsis.json'])
    # sepsisAmaValueSet = PhenotypeEntity('Sepsis AMA-PCPI', 'valueset', values=['2.16.840.1.113883.17.4077.3.2033'])
    # redBloodValueSet = PhenotypeEntity('Red Blood Cells Example', 'valueset',
    #                                   values=['E0150', 'E0161', 'E0178'],
    #                                   library='ISBT')
    Sepsis = PhenotypeDefine("Sepsis", "termset", values=['Sepsis', 'Systemic infection'])
    Ventilator = PhenotypeDefine("Ventilator", "termset", values=['ventilator', 'vent'])
    # ProviderNotes = PhenotypeDefine("ProviderNotes", "documentset",
    #                                 library="Clarity",
    #                                 funct="createReportTagList",
    #                                 arguments=["Physician", "Nurse", "Note", "Discharge Summary"])
    ProviderNotes = PhenotypeDefine("ProviderNotes", "documentset",
                                    library="Clarity",
                                    funct="createDocumentSet",
                                    named_arguments={
                                        "filter_query": "subject:(55672 OR 77614 OR 31942 OR 67906 OR 30202)",
                                        "report_types": [
                                            "Discharge summary"
                                        ],
                                        "report_tags": [],
                                        "query": "report_text:smok* OR cigar* OR etoh"
                                    })
    RadiologyNotes = PhenotypeDefine("Radiology", "documentset",
                                     library="Clarity",
                                     funct="createReportTagList",
                                     arguments=["Radiology"])

    RBCTransfusionPatients = PhenotypeDefine('RBCTransfusionPatients', 'cohort',
                                             library='OHDSI',
                                             funct='getCohortByName',
                                             arguments=['RBC New Exposures'])

    onVentilator = PhenotypeEntity('onVentilator', 'define',
                                   library='ClarityNLP',
                                   funct='TermFinder',
                                   named_arguments={
                                       "termsets": ['Ventilator'],
                                       "documentsets": ['ProviderNotes']
                                   })

    hasSepsis = PhenotypeEntity('hasSepsis', 'define',
                                library='Clarity',
                                funct='ProviderAssertion',
                                named_arguments={
                                    "termsets": ['Sepsis'],
                                    "documentsets": [
                                        'ProviderNotes',
                                        "Radiology"
                                    ]
                                })
    #
    # transfusionEvent = PhenotypeEntity('transfusionEvent', 'define',
    #                                    library='OHDSI',
    #                                    funct='getCohortIndexDateTime',
    #                                    arguments=["RBC Tranfusion Patients"])

    SepsisState = PhenotypeOperations('SepsisState', 'OR', ['onVentilator', 'hasSepsis'], final=True)

    # SepsisPostTransfusion = PhenotypeOperations('SepsisPostTransfusion', 'AND',
    #                                             [
    #                                                 'SepsisState',
    #                                                 PhenotypeOperations('SepsisPostTransfusion_inner1',
    #                                                                     'LESS_THAN',
    #                                                                     [
    #                                                                         PhenotypeOperations(
    #                                                                             'SepsisPostTransfusion_inner2',
    #                                                                             'SUBTRACT',
    #                                                                             [
    #                                                                                 'SepsisState.report_date',
    #                                                                                 'transfusionEvent.procedure_date'
    #                                                                             ]),
    #                                                                         '72H'
    #                                                                     ]
    #                                                                     )
    #                                             ],
    #                                             final=True)
    sepsisPhenotype = PhenotypeModel(owner='jduke',
                                     phenotype=ptype,
                                     description='Sepsis definition derived from Murff HJ, FitzHenry F, Matheny ME, et al. Automated identification of postoperative complications within an electronic medical record using natural language processing. JAMA. 2011;306(8):848-855.',
                                     data_models=[using_omop],
                                     includes=[clarity_core, ohdsi_helpers],
                                     code_systems=[omop, isbt],
                                     value_sets=[],
                                     term_sets=[Ventilator, Sepsis],
                                     document_sets=[ProviderNotes, RadiologyNotes],
                                     population='RBC Transfusion Patients',
                                     data_entities=[
                                         onVentilator, hasSepsis
                                     ],
                                     operations=[
                                         SepsisState
                                     ])
    return sepsisPhenotype


# TODO is it a logical operation or a 'job'


if __name__ == "__main__":
    p = get_sample_phenotype()
    sorted(p.operations, key=lambda o: o['final'])
    json = p.to_json()

    print(json)

# conceptset or termset as inputs for entities
# where or as for operations
