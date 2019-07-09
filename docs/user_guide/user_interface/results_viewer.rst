.. _ui_results_viewer:

Results Viewer
==============

The Results viewer is designed to give you a comprehensive look at all of the results that have come from a query you have run on your ClarityNLP instance.

The first screen will provide with the first 20 jobs that have been run. You can navigate the results by using the Next page and Previous button to the top right of the list. Each Job has many interactions associated with it. The columns available for each job is:

- The name of the query that was run
- The date the query was run
- The current status of the job, *If not complete* this will appear as a link that will take you to the luigi link for that job
- The cohort size for that particular query
- The accuracy score associated with that query
- Download links for the job that includes CSVs of:
    - Results
    - Cohort
    - Annotations
- Actions that can be taken on the job, which includes:
    - Viewing the text representation of the query
    - Viewing the JSON representation of the query
    - Deleting the job

NOTE: Deleting a job is permanent and cannot be undone.

.. image:: ./images/claritynlp_viewer_1.png
.. image:: ./images/claritynlp_viewer_5.png
.. image:: ./images/claritynlp_viewer_4.png
.. image:: ./images/claritynlp_viewer_12.png

This list is also searchable based on the search criteria entered in the search field above.

.. image:: ./images/claritynlp_viewer_13.png

To delve deeper into a job, click on that job's row in the list. This will bring you to a screen where you can see the multiple patients that came back with results from the query. You can also see the number of events that were recognized for each of those patients.

.. image:: ./images/claritynlp_viewer_2.png

If no results were found for a query, a blank screen will appear.

.. image:: ./images/claritynlp_viewer_8.png

To the top right of the page, you can cycle through the Explore view, Feature view, and Cohort view. The Feature view and Cohort view will appear as tables that you can scroll through. The Explore view is the default.

.. image:: ./images/claritynlp_viewer_3.png
.. image:: ./images/claritynlp_viewer_11.png

If you want to view the results for a patient, click that patient's row in the list. This will bring you to a screen where you can view each result individually.

.. image:: ./images/claritynlp_viewer_10.png

The Next Page and Previous buttons to the top right will cycle you through the various patients for that job. 

To the left of the page, you can view NLPQL features that have results. Clicking one of these features, will filter the results that you see to the right of the page. All results are populated by default.

.. image:: ./images/claritynlp_viewer_9.png

Each result has a feature, an outcome, and a sentence associated with it. The feature is the feature from the query that provided the result. The outcome is a small synopsis of what the algorithm found based on a patient's document. The sentence is the sentence from the report that the outcome was found. 

Each result also has a number of actions that you can take to help improve the functionality of the algorithms used to provide results. You can:

- Click the check if the result was helpful
- Click the X if the result was not helpful
- Click the notepad to leave a comment about the result

.. image:: ./images/claritynlp_viewer_6.png

To see the full report where a result was found, you can click on the sentence.

.. image:: ./images/claritynlp_viewer_7.png
