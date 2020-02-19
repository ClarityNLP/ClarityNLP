import psycopg2
import psycopg2.extras
import util
import sys
import traceback
import simplejson as json
from claritynlp_logging import log, ERROR, DEBUG


try:
    from .base_model import BaseModel
    from .pipeline_config import PipelineConfig
except Exception as e:
    log(e)
    from base_model import BaseModel
    from pipeline_config import PipelineConfig


class PhenotypeDefine(dict):

    def __init__(self, name: str, declaration: str, alias: str = '',
                 version: str = '', library: str = 'ClarityNLP',
                 named_arguments: dict=None, arguments: list=None,
                 funct: str = '', values: list = None, description: str = '',
                 concept: str = ''):

        if named_arguments is None:
            named_arguments_init = dict()
        else:
            named_arguments_init = named_arguments

        if arguments is None:
            arguments_init = list()
        else:
            arguments_init = arguments

        if values is None:
            values_init = list()
        else:
            values_init = values

        dict.__init__(self, name=name, declaration=declaration, version=version,
                      alias=alias, arguments=arguments_init,
                      named_arguments=named_arguments_init, library=library,
                      funct=funct, values=values_init,
                      description=description, concept=concept)


class PhenotypeEntity(dict):

    def __init__(self, name: str, declaration: str, alias: str = '', version: str = '',
                 library: str = '', named_arguments: dict = None,
                 arguments: list = None, funct: str = '', values: list = None,
                 description: str = '', concept: str = '', final: bool = False,
                 raw_text: str = '', job_results: list = None):

        if named_arguments is None:
            named_arguments_init = dict()
        else:
            named_arguments_init = named_arguments

        if arguments is None:
            arguments_init = list()
        else:
            arguments_init = arguments

        if values is None:
            values_init = list()
        else:
            values_init = values

        if job_results is None:
            job_results_init = list()
        else:
            job_results_init = job_results

        dict.__init__(self, name=name, declaration=declaration, version=version,
                      alias=alias, arguments=arguments_init, named_arguments=named_arguments_init,
                      library=library, funct=funct, values=values_init,
                      description=description, concept=concept, final=final,
                      raw_text=raw_text, job_results=job_results_init)


class PhenotypeOperations(dict):

    def __init__(self, name: str, action: str, data_entities: list, final: bool = False,
                 raw_text: str = '', normalized_expr: str = ''):
        dict.__init__(self, name=name, action=action, data_entities=data_entities, final=final,
                      raw_text=raw_text, normalized_expr=normalized_expr)


class PhenotypeModel(BaseModel):

    # data_models maps to 'using'
    def __init__(self, name: str = '', description: str = '', owner: str = 'claritynlp', context: str = 'Patient',
                 population: str='All', phenotype=None, data_models: list = None, includes: list = None,
                 code_systems: list = None, value_sets: list = None, term_sets: list = None,
                 document_sets: list = None, data_entities: list = None, cohorts: list = None,
                 operations: list = None, debug=False, limit: int = 0, nlpql: str = '',
                 phenotype_id=1, valid=True):
        self.owner = owner
        self.name = name
        self.description = description
        self.population = population
        self.context = context
        self.phenotype = phenotype
        self.valid = valid
        if data_models is None:
            self.data_models = list()
        else:
            self.data_models = data_models
        if includes is None:
            self.includes = list()
        else:
            self.includes = includes
        if code_systems is None:
            self.code_systems = list()
        else:
            self.code_systems = code_systems
        if value_sets is None:
            self.value_sets = list()
        else:
            self.value_sets = value_sets
        if term_sets is None:
            self.term_sets = list()
        else:
            self.term_sets = term_sets
        if document_sets is None:
            self.document_sets = list()
        else:
            self.document_sets = document_sets
        if data_entities is None:
            self.data_entities = list()
        else:
            self.data_entities = data_entities
        if cohorts is None:
            self.cohorts = list()
        else:
            self.cohorts = cohorts
        if operations is None:
            self.operations = list()
        else:
            self.operations = operations
        self.debug = debug
        self.limit = limit
        self.nlpql = nlpql
        self.phenotype_id = phenotype_id


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
        log('failed to insert phenotype mapping')
        traceback.print_exc(file=sys.stdout)
    finally:
        conn.close()

    return 'done'


def insert_phenotype_model(phenotype: PhenotypeModel, connection_string: str):
    conn = psycopg2.connect(connection_string)
    cursor = conn.cursor()
    p_id = -1

    try:
        name = ''
        if phenotype.phenotype:
            if 'name' in phenotype.phenotype:
                if len(phenotype.phenotype['name']) > 250:
                    name = phenotype.phenotype['name'][0:249]
                else:
                    name = phenotype.phenotype['name']

        if len(name) == 0:
            if len(phenotype.description) > 250:
                name = phenotype.description[0:249]
            else:
                name = phenotype.description
        name = name.replace('"', '')
        p_json = phenotype.to_json()
        cursor.execute("""
                      INSERT INTO nlp.phenotype(owner, config, name, description, nlpql, date_created) 
                      VALUES(%s, %s, %s, %s, %s, current_timestamp) RETURNING phenotype_id
                      """, (phenotype.owner, p_json, name, phenotype.description, phenotype.nlpql))

        p_id = cursor.fetchone()[0]
        conn.commit()

    except Exception as ex:
        log('failed to insert phenotype')
        traceback.print_exc(file=sys.stdout)
    finally:
        conn.close()

    return p_id


def update_phenotype_model(phenotype: PhenotypeModel, connection_string: str):
    conn = psycopg2.connect(connection_string)
    cursor = conn.cursor()

    try:
        if 'phenotype_id' not in phenotype or phenotype['phenotype_id'] < 0:
            return False
        p_json = phenotype.to_json()
        cursor.execute("""
                      UPDATE nlp.phenotype set config=%s WHERE phenotype_id = %s
                      """, (p_json, str(phenotype.phenotype_id)))

        conn.commit()
        success = True
    except Exception as ex:
        log('failed to insert phenotype')
        traceback.print_exc(file=sys.stdout)
        success = False
    finally:
        conn.close()

    return success


def phenotype_structure(phenotype_id: int, connection_string: str):
    conn = psycopg2.connect(connection_string)
    cursor = conn.cursor()
    hierarchy = dict()

    try:

        cursor.execute("""SELECT config FROM nlp.phenotype WHERE phenotype_id = %s""",
                       [phenotype_id])
        config = json.loads(cursor.fetchone()[0])

        if 'operations' in config:
            final_ops = list(filter(lambda o: o['final'], config['operations']))
            ops = {o['name']: o for o in config['operations']}
        else:
            final_ops = list()
            ops = dict()

        if 'data_entities' in config:
            final_des = list(filter(lambda o: o['final'], config['data_entities']))
            des = {o['name']: o for o in config['data_entities']}
        else:
            des = dict()
            final_des = dict()

        hierarchy['config'] = config
        hierarchy['finals'] = (final_ops + final_des)
        hierarchy['operations'] = ops
        hierarchy['data_entities'] = des

    except Exception as ex:
        traceback.print_exc(file=sys.stdout)
    finally:
        conn.close()

    return hierarchy


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
        traceback.print_exc(file=sys.stdout)
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
        traceback.print_exc(file=sys.stdout)
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
                                        "query": "%s:smok* OR cigar* OR etoh" % util.solr_text_field
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
                                    ],
                                    "code": "91302008",
                                    "codesystem": "SNOMED"
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
    json_str = p.to_json()

    log(json_str)

    hier = phenotype_structure(10144, util.conn_string)
    log(hier)

# conceptset or termset as inputs for entities
# where or as for operations
