.. _customtaskalgo:

Custom Task Algorithms
======================

Building custom task algorithms in ClarityNLP is a way to create custom algorithms and include external libraries that are callable from NLPQL. To begin creating custom task algorithms, you need a few things to get started.

Create a Python Class
---------------------
In ``nlp/custom_tasks``, create a new Python class that extends ``BaseTask``. ``BaseTask`` is a class that sets up the data, context and connections needed to read and write data in ClarityNLP.
See the source code for ``BaseTask`` at ``nlp/tasks/task_utilities.py``. You can start with the sample below and copy and paste the basic structure that you need for a custom task.

.. code-block:: python

    from tasks.task_utilities import BaseTask
    from pymongo import MongoClient

    class SampleTask(BaseTask):
        task_name = "MyCustomTask"

        def run_custom_task(self, temp_file, mongo_client: MongoClient):
            for doc in self.docs:

                # you can get sentences and text through these utility methods
                text = self.get_document_text(doc)
                sentences = self.get_document_sentences(doc)

                # put your custom algorithm here, save your output to a dictionary, and write results below
                obj = {
                    'foo': 'bar',
                    'sentence_one': sentences[0]
                }

                # writing results
                self.write_result_data(temp_file, mongo_client, doc, obj)

                # writing to log (optional)
                self.write_log_data("DONE", "done writing sample data")




Task Name
---------
``task_name`` is important to include in your SampleTask if you want a user-friendly name to be called from NLPQL.
In this example, the task name is ``MyCustomTask``, but if a custom task wasn't specified, the task name would be ``SampleTask``.
Also, it's important to be aware with naming that you can overwrite other custom tasks and even core ClarityNLP tasks (which may be the desired outcome). So in most cases, you'll want to provide a unique name.


Running a Custom Task
---------------------
The ClarityNLP engine will automatically create a distributed job and assign a set of documents to each worker task. Knowing that, there are just a few things to do to create custom tasks. You'll need to implement the ``run_custom_task`` function in your task.
That will give you access to the ``self`` parameter which has attributes from the job and the set of documents your algorithm will run on. You don't need to worry about them too much, but know they are accessible in your custom task.


You also have access to a ``temp_file`` which is provided by Luigi. It's not necessarily used by ClarityNLP, but you may wish to use it for some logging purpose (logging will be discussed more below). In addition, you have a ``mongo_client`` connection that is opened and closed for you, however you'll need access to this object when you're writing output for your ClarityNLP NLPQL.


Iterating over Documents
------------------------
Since you are responsible for a set of documents, you need to get the list of documents which has been assigned to this worker. This is callable by using ``self.docs`` and should be iterable in Python.

Per document (or ``doc``), there are few helper functions available for you.

* ``self.get_document_text(doc)`` - gets the text of document as a string
* ``self.get_document_sentences(doc)`` - gets a list of the sentences in a document, parsed with the default ClarityNLP sentence segmentor


Accessing Custom Variables
--------------------------
If you have custom parameters in your NLPQL, you can access them via the ``custom_arguments`` dictionary in your pipeline config.

.. code-block:: python

    my_value = self.pipeline_config.custom_arguments['my_value']


Saving Results
--------------
All data that ClarityNLP uses in NLPQL needs to eventually end up in MongoDB. ``BaseTask`` provides two types of hooks, depending on whether you have a single object or a list of objects. Both return the new unique id (or ids) from MongoDB.

* ``self.write_result_data(temp_file, mongo_client, doc, obj)`` - saves results where ``obj`` is a Python ``dict``
* ``self.write_multiple_result_data(temp_file, mongo_client, doc, obj_list)`` - saves results where ``obj_list`` is a Python ``list`` or ``set`` (implies multiple results per document)


Logging and Debugging
---------------------
ClarityNLP provides two means for logging and debugging your custom tasks. Most commonly you will use the first method, where you pass in a **status** and **description text**.
This is written to the Postgres database, and accessible when users call the status function on their NLPQL jobs.

.. code-block:: python

    self.write_log_data("DONE!", "done writing sample data")

The second is less common, but may be desirable in certain cases, which is writing to the ``temp_file`` used by Luigi, e.g.:

.. code-block:: python

    temp_file.write("Some pretty long message that maybe I don't want to show to users")

This is written to the file system and generally not accessible to users via APIs.


Using Custom Collectors
-----------------------
Collectors in ClarityNLP are similar to the reduce step in map-reduce jobs. They can be implemented similar to custom tasks, except their purpose is generally to summarize across all the data generated in the parallelized Luigi tasks.
To utilize the collector, extend the ``BaseCollector`` class, and make sure your ``collector_name`` in that class is the same as your ``task_name`` in your custom task.

.. code-block:: python

    class MyCustomCollector(BaseCollector):
        collector_name = 'cool_custom_stuff'

        def custom_cleanup(self, pipeline_id, job, owner, pipeline_type, pipeline_config, client, db):
            print('custom cleanup (optional)')

        def run_custom_task(self, pipeline_id, job, owner, pipeline_type, pipeline_config, client, db):
            print('run custom task collector')
            # TODO write out some summary stats to mongodb


    class MyCustomTask(BaseTask):
        task_name = 'cool_custom_stuff'

        def run_custom_task(self, temp_file, mongo_client: MongoClient):
            print('run custom task')

            for doc in self.docs:
                # TODO write out some data to mongodb about these docs


Collectors often are not needed, but may be necessary for certain algorithm implementations.

Setting up the Python Package
-----------------------------
ClarityNLP automatically discovers any classes in the ``custom_task`` package. However, besides saving your Python file in ``custom_tasks``, you just need to make sure it's included in the ``custom_tasks`` package by adding it to ``nlp/custom_tasks/__init__.py``, following the example:

.. code-block:: python

    from .SampleTask import SampleTask


Calling Custom Algorithms from NLPQL
------------------------------------
To run your custom algorithm in NLPQL, you just need to call it by name as a function like the example below, and make sure to pass in any variables needed for the config and Solr query.

.. code-block:: python

    define sampleTask:
      Clarity.MyCustomTask({
        documentset: [ProviderNotes],
        "my_custom_argument": 42
      });

Custom Algorithm or External Library?
-------------------------------------
There aren't too many limitations on what you build inside of custom tasks and collectors, given that it's a something that can input text, and output a Python object. This is a powerful feature that will allow you to integrate many types of capabilities into ClarityNLP!


Other Conventions
-----------------
While the previous sections contain the main items you need to create custom task algorithms in ClarityNLP, here's some other information that might be useful.

* **Default Value**: Or using ``value`` as the default field. In NLPQL, when no field name is specified, it will default to ``value``. This means that you may want to provide a ``value`` field in your resulting object that gets saved to MongoDB, so that there's a default value
* **Sentences**: While there's no requirement to parse or run your algorithm at the sentence level, it is useful for scoping and user validation. Therefore, in most of the core ClarityNLP algorithms, output ``sentence`` is part of the result, and you may wish to follow this paradigm
* **Metadata**: All the metadata from the job is automatically saved for you, however you may have additional metadata you want to save from your algorithm or source data
