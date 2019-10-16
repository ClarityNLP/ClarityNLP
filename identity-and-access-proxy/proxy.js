const http = require('http');
const httpProxy = require('http-proxy');
const HttpProxyRules = require('http-proxy-rules');
const request = require('request');
const jwksClient = require('jwks-rsa');
var jwt = require('jsonwebtoken');
const url = require('url');

const {
  PROTOCOL,
  DOMAIN,
  DASHBOARD_CLIENT_SUBDOMAIN,
  INGEST_CLIENT_SUBDOMAIN,
  RESULTS_CLIENT_SUBDOMAIN,
  IDENTITY_PROVIDER_HOSTNAME,
  IDENTITY_PROVIDER_CONTAINER_PORT
} = process.env;

const allowedOrigins = [
  `${PROTOCOL}://${DASHBOARD_CLIENT_SUBDOMAIN}.${DOMAIN}`,
  `${PROTOCOL}://${INGEST_CLIENT_SUBDOMAIN}.${DOMAIN}`,
  `${PROTOCOL}://${RESULTS_CLIENT_SUBDOMAIN}.${DOMAIN}`
];

// Set up proxy rules instance
var proxyRules = new HttpProxyRules({
  rules: {
    // SOLR-API
    '/solr/(.*)': 'http://nlp-solr:8983/solr/$1',
    // NLP-API
    '/nlp/library': 'http://nlp-api:5000/library',
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
    '/nlp/nlpql_expander': 'http://nlp-api:5000/nlpql_expander',
    '/nlp/add_query': 'http://nlp-api:5000/add_query',
    '/nlp/nlpql': 'http://nlp-api:5000/nlpql',
    '/nlp/phenotype': 'http://nlp-api:5000/phenotype',
    '/nlp/phenotype_results_by_id/(.+)':
      'http://nlp-api:5000/phenotype_results_by_id/$1',
    '/nlp/status/(.+)': 'http://nlp-api:5000/status/$1',
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
    '/nlpaas/(.*)': 'http://nlpaas:5000/$1',
    '/socket.io': 'ws://ingest-api:1337/socket.io' //TODO rename ingest to consolidated socket server
  }
});

const whitelist = new HttpProxyRules({
  rules: {
    '/__getcookie': 'http://ingest-api:1337/__getcookie'
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

  //check whitelist
  const whitelistTarget = whitelist.match(req);

  console.log('whitelistTarget: ',whitelistTarget);

  if (whitelistTarget) {
    return proxy.web(
      req,
      res,
      {
        target: whitelistTarget
      },
      function(err) {
        console.log('proxy.web error');
        console.log(err);
        sendError(res, err);
      }
    );
  }

  var client = jwksClient({
    jwksUri:
      `http://${IDENTITY_PROVIDER_HOSTNAME}:${IDENTITY_PROVIDER_CONTAINER_PORT}/.well-known/openid-configuration/jwks`
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
  const target = proxyRules.match(req);

  proxy.ws(
    req,
    socket,
    head,
    {
      target: target
    },
    function(err) {
      console.log('err: ', err);
    }
  );
});

proxyServer.listen(6010);
