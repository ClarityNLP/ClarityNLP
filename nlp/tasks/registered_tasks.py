from tasks import *

registered_pipelines = {
    "TermFinder": TermFinderBatchTask,
    "Finder": TermFinderBatchTask,
    "Assertion": ProviderAssertionBatchTask,
    "ProviderAssertion": ProviderAssertionBatchTask,
    "MeasurementFinder": MeasurementFinderTask,
    "MeasurementExtractor": MeasurementFinderTask,
    "MeasurementExtraction": MeasurementFinderTask,
    "ValueExtractor": ValueExtractorTask,
    "ValueExtraction": ValueExtractorTask,
    "NamedEntityRecognition": NERTask,
    "NER": NERTask,
    "POSTagger": POSTaggerTask
}
