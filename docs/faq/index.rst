.. _faqindex:

.. |br| raw:: html

   <br />

Frequently Asked Questions (FAQ)
================================

1. **How can I check the syntax of my NLPQL file without actually running it?**

   Send your NLPQL file via HTTP POST to the
   :ref:`nlpql_tester<nlpql_tester_api>` API endpoint. ClarityNLP will return a
   a JSON representation of your file if the syntax is correct. If a syntax
   error is present, ClarityNLP will print an error message and no JSON will
   be returned.
  
   |br|
  
2. **If I'm using the Docker version of ClarityNLP, how do I verify that all**
   **the supporting Docker containers are up and running?**

   Open a terminal and run the command ``docker ps``.  The status of each
   container will be printed to stdout. Each container should report a
   status message of ``Up n seconds``, where n is an integer, if the container
   is fully initialized and running.


