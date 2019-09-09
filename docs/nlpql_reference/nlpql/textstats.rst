.. _textstats:


Clarity.TextStats
=================

Description
-----------

Task that uses `textacy <https://github.com/chartbeat-labs/textacy/blob/master/textacy/text_stats.py>`_ to get aggregate statistics about the text.

Example
-------
::

    Clarity.TextStats({
      documentset: [ProviderNotes]
    });


Extends
-------
:ref:`base_task`


Arguments
---------

=====================  ===================  ========= ======================================
         Name                 Type          Required                  Notes
=====================  ===================  ========= ======================================
termset                :ref:`termset`       No
documentset            :ref:`documentset`   No
cohort                 :ref:`cohort`        No
group_by               str                  No        Default = `report_type`, the field that statistics be grouped on.
=====================  ===================  ========= ======================================



Results
-------


==========================  ================  ==========================================
         Name                    Type                             Notes
==========================  ================  ==========================================
avg_word_cnt                float             Average word count
avg_grade_level             float             Average Flesch Kincaid grade level
avg_sentences               float             Average number of sentences
avg_long_words              float             Average number of long words
avg_polysyllable_words      float             Average number of polysyllabic words
==========================  ================  ==========================================


Collector
---------
:ref:`base_collector`
