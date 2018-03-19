try:
    from .base_model import BaseModel
    from .pipeline_config import PipelineConfig
except Exception as e:
    print(e)
    from base_model import BaseModel
    from pipeline_config import PipelineConfig


class PhenotypeDefine(dict):

    def __init__(self, name: str, declaration: str, alias: str = '', version: str = '', library: str = '',
                 named_arguments: dict = dict(),
                 arguments: list = list(), function: str = '', values: list = list(), description: str = '',
                 concept: str = ''):
        dict.__init__(self, name=name, declaration=declaration, version=version, alias=alias, arguments=arguments,
                      named_arguments=named_arguments, library=library, function=function, values=values,
                      description=description, concept=concept)


class PhenotypeEntity(dict):

    def __init__(self, name: str, declaration: str, alias: str = '', version: str = '', library: str = '',
                 named_arguments: dict = dict(),
                 arguments: list = list(), function: str = '', values: list = list(), description: str = '',
                 concept: str = '', final: bool = False, raw_text: str = ''):
        dict.__init__(self, name=name, declaration=declaration, version=version, alias=alias, arguments=arguments,
                      named_arguments=named_arguments, library=library, function=function, values=values,
                      description=description, concept=concept, final=final, raw_text=raw_text)


class PhenotypeOperations(dict):

    def __init__(self, name: str, action: str, data_entities: list, final: bool = False, raw_text: str = ''):
        dict.__init__(self, name=name, action=action, data_entities=data_entities, final=final, raw_text=raw_text)


class PhenotypeModel(BaseModel):

    # versions maps to 'using'
    def __init__(self, owner: str, description: str = '', context: str = 'Patient', population: str = 'All',
                 phenotype: PhenotypeEntity = None, versions: list = list(),
                 includes: list = list(), code_systems: list = list(),
                 value_sets: list = list(), term_sets: list = list(),
                 document_sets: list = list(), data_entities: list = list(),
                 operations: list = list()):
        self.owner = owner
        self.description = description
        self.population = population
        self.context = context
        self.versions = versions
        self.phenotype = phenotype
        self.includes = includes
        self.code_systems = code_systems
        self.value_sets = value_sets
        self.term_sets = term_sets
        self.document_sets = document_sets
        self.data_entities = data_entities
        self.operations = operations


# TODO is it a logical operation or a 'job'


if __name__ == "__main__":
    lib = PhenotypeDefine('Sepsis', 'library', version='1')
    using_omop = PhenotypeDefine('OMOP', 'datamodel', version='5.3')
    clarity_core = PhenotypeDefine('ClarityCore', 'include', version='1.0', alias='Clarity')
    ohdsi_helpers = PhenotypeDefine('OHDSIHelpers', 'include', version='1.0', alias='OHDSI')
    omop = PhenotypeDefine('OMOP', 'codesystem', values=['http://omop.org'])
    isbt = PhenotypeDefine('ISBT', 'codesystem', values=['https://www.iccbba.org'])
    Sepsis = PhenotypeDefine('Sepsis', 'valueset', library='OHDSI',
                             function='getConceptSet',
                             arguments=['assets/Sepsis.json'])
    # sepsisAmaValueSet = PhenotypeEntity('Sepsis AMA-PCPI', 'valueset', values=['2.16.840.1.113883.17.4077.3.2033'])
    # redBloodValueSet = PhenotypeEntity('Red Blood Cells Example', 'valueset',
    #                                   values=['E0150', 'E0161', 'E0178'],
    #                                   library='ISBT')

    Ventilator = PhenotypeDefine("Ventilator", "termsetset", values=['ventilator', 'vent'])
    ProviderNotes = PhenotypeDefine("ProviderNotes", "documentset",
                                    library="Clarity",
                                    function="createDocumentList",
                                    arguments=["'Physician' OR 'Nurse' OR 'Note' OR 'Discharge Summary'"])

    RBCTransfusionPatients = PhenotypeDefine('RBCTransfusionPatients', 'cohort',
                                             library='OHDSI',
                                             function='getCohortByName',
                                             arguments=['RBC New Exposures'])

    onVentilator = PhenotypeEntity('onVentilator', 'define',
                                   library='Clarity',
                                   function='TermFinder',
                                   named_arguments={
                                       "termsets": ['Ventilator'],
                                       "documentsets": ['ProviderNotes']
                                   })

    hasSepsis = PhenotypeEntity('hasSepsis', 'define',
                                library='Clarity',
                                function='ProviderAssertion',
                                named_arguments={
                                    "termsets": ['Sepsis'],
                                    "documentsets": [
                                        'ProviderNotes',
                                        "Radiology"
                                    ]
                                })

    transfusionEvent = PhenotypeEntity('transfusionEvent', 'define',
                                       library='OHDSI',
                                       function='getCohortIndexDateTime',
                                       arguments=["RBC Tranfusion Patients"])

    SepsisState = PhenotypeOperations('SepsisState', 'OR', ['onVentilator', 'hasSepsis'])

    SepsisPostTransfusion = PhenotypeOperations('SepsisPostTransfusion', 'AND',
                                                [
                                                    'SepsisState',
                                                    PhenotypeOperations('SepsisPostTransfusion_inner1',
                                                                        'LESS_THAN',
                                                                        [
                                                                            PhenotypeOperations(
                                                                                'SepsisPostTransfusion_inner2',
                                                                                'MINUS',
                                                                                [
                                                                                    'SepsisState.report_date',
                                                                                    'transfusionEvent.procedure_date'
                                                                                ]),
                                                                            '72H'
                                                                        ]
                                                                        )
                                                ],
                                                final=True)
    sepsisPhenotype = PhenotypeModel('jduke',
                                     phenotype=lib,
                                     description='Sepsis definition derived from Murff HJ, FitzHenry F, Matheny ME, et al. Automated identification of postoperative complications within an electronic medical record using natural language processing. JAMA. 2011;306(8):848-855.',
                                     versions=[using_omop],
                                     includes=[clarity_core, ohdsi_helpers],
                                     code_systems=[omop, isbt],
                                     value_sets=[Sepsis],
                                     term_sets=[Ventilator],
                                     document_sets=[ProviderNotes],
                                     population='RBC Transfusion Patients',
                                     data_entities=[
                                         onVentilator, hasSepsis, transfusionEvent
                                     ],
                                     operations=[
                                         SepsisState, SepsisPostTransfusion
                                     ])

    json = sepsisPhenotype.to_json()
    print(json)


# conceptset or termset as inputs for entities
# where or as for operations