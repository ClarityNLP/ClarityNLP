.. _base_collector:

BaseCollector
=============
The base class for ClarityNLP aggregate tasks. Only gets called after all the other tasks of its related type are complete.



Functions
---------

run(pipeline_id, job, owner, pipeline_type, pipeline_config)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Main function that runs the collector.

----

run_custom_task(pipeline_id, job, owner, pipeline_type, pipeline_config, client, db)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Primary function where custom implementation of the collector is written.

----

custom_cleanup(pipeline_id, job, owner, pipeline_type, pipeline_config, client, db)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


Run custom custom cleanup after collector has run.

----


cleanup(pipeline_id, job, owner, pipeline_type, pipeline_config)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Main cleanup task that marks job as complete and runs custom cleanup tasks after collector is completed.

