Retrieve OAuth2 Access Token
============================

The steps below will help you retrieve an OAuth2 access token for use with different http libraries/tools such as Postman and cURL.

In both the development and production environments clients can initiate an OAuth2 flow with the following parameters:

* :code:`grant_type` with the value :code:`client_credentials`
* :code:`client_id` with "cli"
* :code:`client_secret` with the value of the :code:`CLIENT_CLI_SECRET` environment variable
* :code:`scope` with a space-delimited list of requested scope permissions

Postman Example
---------------

1. In the request building panel click the "Authorization" tab.
2. In the "Type" dropdown, select "OAuth 2.0"
3. Click "Get New Access Token"
4. Type a :code:`Token Name`, i.e. "ClarityNLP"
5. Choose "Client Credentials" as the :code:`Grant Type`
6. Set :code:`Access Token URL` as "https://idp.claritynlp.dev/connect/token". Change domain in production.
7. Set :code:`Client ID` as "cli"
8. Set :code:`Client Secret` as value of :code:`CLIENT_CLI_SECRET` environment variable
9. Set :code:`Scope` as space-delimited list of requested scope permissions, i.e. "ingest_api nlp_api solr_api"
10. Set :code:`Client Authentication` as "Send as Basic Auth header"

cURL Example
------------

::

  curl -LkX POST -d "client_id=cli&client_secret=secret&grant_type=client_credentials" https://idp.claritynlp.dev/connect/token
