from tasks import *
from custom_tasks import *
import importlib
import os
from pathlib import Path
import sys
import inspect
import pkgutil
from importlib import import_module


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
    "POSTagger": POSTaggerTask,
    "TNMStager": TNMStagerTask,
    "ngram": NGramTask
}

registed_collectors = {
    "ngram": NGramCollector
}


def register_pipeline_task(task_name, task_cls):
    # TODO checks if valid type
    if task_name and len(task_name) > 0:
        if task_name in registered_pipelines:
            print("WARNING: Overwriting existing pipeline %s" % task_name)
        registered_pipelines[task_name] = task_cls


def register_tasks():
    for (_, name, _) in pkgutil.iter_modules(path=["custom_tasks"]):

        imported_module = import_module('custom_tasks.' + name, package=__name__)

        for i in dir(imported_module):
            attribute = getattr(imported_module, i)

            if inspect.isclass(attribute) and issubclass(attribute, BaseTask):
                if not i == 'BaseTask':
                    setattr(sys.modules[__name__], name, attribute)

                    task_name = attribute.task_name
                    if task_name == "ClarityNLPLuigiTask":
                        task_name = i
                    registered_pipelines[task_name] = attribute

