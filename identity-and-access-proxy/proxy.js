const http = require('http');
const httpProxy = require('http-proxy');
const HttpProxyRules = require('http-proxy-rules');
const request = require('request');
const jwksClient = require('jwks-rsa');
var jwt = require('jsonwebtoken');
const url = require('url');

const allowedOrigins = [
  'dashboard.clarity.localhost',
  'ingest.clarity.localhost',
  'viewer.clarity.localhost',
  'http://dashboard.clarity.localhost',
  'http://ingest.clarity.localhost',
  'http://viewer.clarity.localhost',
  'localhost'
];

// Set up proxy rules instance
var proxyRules = new HttpProxyRules({
  rules: {
    // NLP-API
    '/api/nlp/pipeline_types': 'http://nlp-api:5000/pipeline_types', //NLP-API --> GET pipeline_types
    '/api/nlp/phenotype_jobs/ALL': 'http://nlp-api:5000/phenotype_jobs/ALL',
    '/api/nlp/phenotype_subjects/(.+)/(.+)': 'http://nlp-api:5000/phenotype_subjects/$1/$2',
    '/api/nlp/phenotype_subject_results/(.+)/(.+)/(.+)': 'http://nlp-api:5000/phenotype_subject_results/$1/$2/$3',
    '/api/nlp/phenotype_job_by_id/(.+)': 'http://nlp-api:5000/phenotype_job_by_id/$1',
    '/api/nlp/phenotype_paged_results/(.+)/(.+)': 'http://nlp-api:5000/phenotype_paged_results/$1/$2',
    '/api/nlp/export_ohdsi': 'http://nlp-api:5000/export_ohdsi',
    '/api/nlp/nlpql_tester': 'http://nlp-api:5000/nlpql_tester',
    '/api/nlp/add_query': 'http://nlp-api:5000/add_query',
    '/api/nlp/nlpql': 'http://nlp-api:5000/nlpql',
    '/api/nlp/phenotype_results_by_id/(.+)': 'http://nlp-api:5000/phenotype_results_by_id/$1',
    '/api/nlp/phenotype_structure/(.+)': 'http://nlp-api:5000/phenotype_structure/$1',
    '/api/nlp/delete_job/(.+)': 'http://nlp-api:5000/delete_job/$1',
    '/api/nlp/kill_job/(.+)': 'http://nlp-api:5000/kill_job/$1',
    '/api/nlp/phenotype_paged_results/(.+)/(.+)': 'http://nlp-api:5000/phenotype_paged_results/$1/$2',
    '/api/nlp/write_nlpql_feedback': 'http://nlp-api:5000/write_nlpql_feedback',
    '/api/nlp/phenotype_feature_results/(.+)/(.+)/(.+)': 'http://nlp-api:5000/phenotype_feature_results/$1/$2/$3',
    '/api/nlp/performance/(.+)': 'http://nlp-api:5000/performance/$1',
    '/api/nlp/stats/(.+)': 'http://nlp-api:5000/stats/$1',
    '/api/nlp/document/(.+)': 'http://nlp-api:5000/document/$1',
    '/api/nlp/job_results/(.+)/phenotype_intermediate': 'http://nlp-api:5000/job_results/$1/phenotype_intermediate',
    '/api/nlp/job_results/(.+)/phenotype': 'http://nlp-api:5000/job_results/$1/phenotype',
    '/api/nlp/job_results/(.+)/annotations': 'http://nlp-api:5000/job_results/$1/annotations',
    // INGEST-API
    '/api/ingest/fields': 'http://ingest-api:1337/fields', //INGEST-API --> GET fields
    '/api/ingest/core': 'http://ingest-api:1337/solr/core', //INGEST-API --> GET solr/core
    '/api/ingest/numDocs': 'http://ingest-api:1337/solr/numDocs', //INGEST-API --> GET solr/numDocs
    '/api/ingest/csv': 'http://ingest-api:1337/ingest/csv', //INGEST-API --> POST /ingest/csv
    '/api/ingest/upload': 'http://ingest-api:1337/upload', //INGEST-API --> POST /upload
    '/api/ingest/(.+)/schedule': 'http://ingest-api:1337/ingest/$1/schedule', //INGEST-API --> POST /ingest/:ingestId/schedule
    '/api/ingest': 'http://ingest-api:1337/ingest', //INGEST-API --> GET /ingest
    '/api/ingest/(.+)/delete': 'http://ingest-api:1337/ingest/$1/delete', //INGEST-API --> GET /ingest/:ingestId/delete
    // DASHBOARD-API
    '/api/dashboard': 'ws://dashboard-api:8750' //DASHBOARD-API --> websocket connection
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
