const http = require('http');
const httpProxy = require('http-proxy');
const HttpProxyRules = require('http-proxy-rules');
const request = require('request');
const jwksClient = require('jwks-rsa');
var jwt = require('jsonwebtoken');
const url = require('url');

const allowedOrigins = [
  'dashboard.claritynlp.dev',
  'ingest.claritynlp.dev',
  'viewer.claritynlp.dev',
  'http://dashboard.claritynlp.dev',
  'http://ingest.claritynlp.dev',
  'http://viewer.claritynlp.dev'
];

// Set up proxy rules instance
var proxyRules = new HttpProxyRules({
  rules: {
    // NLP-API
    '/nlp/pipeline_types': 'http://nlp-api:5000/pipeline_types', //NLP-API --> GET pipeline_types
    '/nlp/phenotype_jobs/ALL': 'http://nlp-api:5000/phenotype_jobs/ALL',
    '/nlp/phenotype_subjects/(.+)/(.+)':
      'http://nlp-api:5000/phenotype_subjects/$1/$2',
    '/nlp/phenotype_subject_results/(.+)/(.+)/(.+)':
      'http://nlp-api:5000/phenotype_subject_results/$1/$2/$3',
    '/nlp/phenotype_job_by_id/(.+)':
      'http://nlp-api:5000/phenotype_job_by_id/$1',
    '/nlp/phenotype_paged_results/(.+)/(.+)':
      'http://nlp-api:5000/phenotype_paged_results/$1/$2',
    '/nlp/export_ohdsi': 'http://nlp-api:5000/export_ohdsi',
    '/nlp/nlpql_tester': 'http://nlp-api:5000/nlpql_tester',
    '/nlp/add_query': 'http://nlp-api:5000/add_query',
    '/nlp/nlpql': 'http://nlp-api:5000/nlpql',
    '/nlp/phenotype_results_by_id/(.+)':
      'http://nlp-api:5000/phenotype_results_by_id/$1',
    '/nlp/phenotype_structure/(.+)':
      'http://nlp-api:5000/phenotype_structure/$1',
    '/nlp/delete_job/(.+)': 'http://nlp-api:5000/delete_job/$1',
    '/nlp/kill_job/(.+)': 'http://nlp-api:5000/kill_job/$1',
    '/nlp/phenotype_paged_results/(.+)/(.+)':
      'http://nlp-api:5000/phenotype_paged_results/$1/$2',
    '/nlp/write_nlpql_feedback': 'http://nlp-api:5000/write_nlpql_feedback',
    '/nlp/phenotype_feature_results/(.+)/(.+)/(.+)':
      'http://nlp-api:5000/phenotype_feature_results/$1/$2/$3',
    '/nlp/performance/(.+)': 'http://nlp-api:5000/performance/$1',
    '/nlp/stats/(.+)': 'http://nlp-api:5000/stats/$1',
    '/nlp/document/(.+)': 'http://nlp-api:5000/document/$1',
    '/nlp/job_results/(.+)/phenotype_intermediate':
      'http://nlp-api:5000/job_results/$1/phenotype_intermediate',
    '/nlp/job_results/(.+)/phenotype':
      'http://nlp-api:5000/job_results/$1/phenotype',
    '/nlp/job_results/(.+)/annotations':
      'http://nlp-api:5000/job_results/$1/annotations',
    '/nlp/delete_query/(.+)': 'http://nlp-api:5000/delete_query/$1',
    '/nlp/get_query/(.+)': 'http://nlp-api:5000/get_query/$1',
    // INGEST-API
    '/ingest/fields': 'http://ingest-api:1337/fields', //INGEST-API --> GET fields
    '/ingest/core': 'http://ingest-api:1337/solr/core', //INGEST-API --> GET solr/core
    '/ingest/numDocs': 'http://ingest-api:1337/solr/numDocs', //INGEST-API --> GET solr/numDocs
    '/ingest/csv': 'http://ingest-api:1337/ingest/csv', //INGEST-API --> POST /ingest/csv
    '/ingest/upload': 'http://ingest-api:1337/upload', //INGEST-API --> POST /upload
    '/ingest/(.+)/schedule': 'http://ingest-api:1337/ingest/$1/schedule', //INGEST-API --> POST /ingest/:ingestId/schedule
    '/ingest': 'http://ingest-api:1337/ingest', //INGEST-API --> GET /ingest
    '/ingest/(.+)/delete': 'http://ingest-api:1337/ingest/$1/delete', //INGEST-API --> GET /ingest/:ingestId/delete
    // DASHBOARD-API
    '/dashboard': 'ws://dashboard-api:8750' //DASHBOARD-API --> websocket connection
  }
});

// Create reverse proxy instance
var proxy = httpProxy.createProxyServer();

var sendError = function(res, err) {
  res.writeHead(500, { 'Content-Type': 'application/json' });
  return res.end(err);
};

// error handling
proxy.on('error', function(err, req, res) {
  sendError(res, err);
});

var enableCors = function(req, res) {
  if (req.headers['access-control-request-method']) {
    res.setHeader(
      'access-control-allow-methods',
      req.headers['access-control-request-method']
    );
  }

  if (req.headers['access-control-request-headers']) {
    res.setHeader(
      'access-control-allow-headers',
      req.headers['access-control-request-headers']
    );
  }

  if (req.headers.origin) {
    res.setHeader('access-control-allow-origin', req.headers.origin);
    res.setHeader('access-control-allow-credentials', 'true');
  }
};

// set header for CORS
proxy.on('proxyRes', function(proxyRes, req, res) {
  enableCors(req, res);
});

// Create http server that leverages reverse proxy instance
// and proxy rules to proxy requests to different targets
const proxyServer = http.createServer(function(req, res) {
  if (req.method === 'OPTIONS') {
    enableCors(req, res);
    res.writeHead(200);
    res.end();
    return;
  }

  var client = jwksClient({
    jwksUri:
      'http://identity-provider:5000/.well-known/openid-configuration/jwks'
  });
  function getKey(header, callback) {
    client.getSigningKey(header.kid, function(err, key) {
      if (err) {
        return callback(err);
      }
      var signingKey = key.publicKey || key.rsaPublicKey;
      callback(null, signingKey);
    });
  }

  let token;

  try {
    token = req.headers.authorization.substring(
      7,
      req.headers.authorization.length
    );
  } catch {
    res.writeHead(400, { 'Content-Type': 'text/plain' });
    return res.end('Malformatted bearer token.');
  }

  jwt.verify(token, getKey, function(err, decoded) {
    if (err) {
      console.error(err);
      res.writeHead(401, { 'Content-Type': 'text/plain' });
      return res.end();
    }

    const target = proxyRules.match(req);

    if (target) {
      return proxy.web(
        req,
        res,
        {
          target: target
        },
        function(err) {
          sendError(res, err);
        }
      );
    }

    res.writeHead(400, { 'Content-Type': 'text/plain' });
    return res.end(
      'The request url and path did not match any of the listed rules.'
    );
  });
});

proxyServer.on('upgrade', function(req, socket, head) {
  proxy.ws(
    req,
    socket,
    head,
    {
      target: 'ws://dashboard-api:8750'
    },
    function(err) {
      console.log('err: ', err);
      // sendError(res, err);
    }
  );
});

proxyServer.listen(6010);
