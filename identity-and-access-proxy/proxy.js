const http = require('http');
const httpProxy = require('http-proxy');
const HttpProxyRules = require('http-proxy-rules');
const request = require('request');
const jwksClient = require('jwks-rsa');
var jwt = require('jsonwebtoken');
const url = require('url');

const allowedOrigins = ['localhost:8500', 'http://localhost:8500', 'localhost'];

// Set up proxy rules instance
var proxyRules = new HttpProxyRules({
  rules: {
    '/api/nlp/pipeline_types': 'http://nlp-api:5000/pipeline_types', //NLP-API --> GET pipeline_types
    '/api/ingest/fields': 'http://ingest-api:1337/fields', //INGEST-API --> GET fields
    '/api/ingest/core': 'http://ingest-api:1337/solr/core', //INGEST-API --> GET solr/core
    '/api/ingest/numDocs': 'http://ingest-api:1337/solr/numDocs', //INGEST-API --> GET solr/numDocs
    '.*/test': 'http://localhost:8080/cool', // Rule (1)
    '.*/test2/': 'http://localhost:8080/cool2/', // Rule (2)
    '/posts/([0-9]+)/comments/([0-9]+)': 'http://localhost:8080/p/$1/c/$2', // Rule (3)
    '/author/([0-9]+)/posts/([0-9]+)/': 'http://localhost:8080/a/$1/p/$2/' // Rule (4)
  }
  // default: 'http://localhost:8080' // default target
});

// Create reverse proxy instance
var proxy = httpProxy.createProxyServer();

var sendError = function(res, err) {
	return res.status(500).send({
		 error: err,
		 message: "An error occured in the proxy"
	});
};

// error handling
proxy.on("error", function (err, req, res) {
	sendError(res, err);
});

var enableCors = function(req, res) {
	if (req.headers['access-control-request-method']) {
		res.setHeader('access-control-allow-methods', req.headers['access-control-request-method']);
	}

	if (req.headers['access-control-request-headers']) {
		res.setHeader('access-control-allow-headers', req.headers['access-control-request-headers']);
	}

	if (req.headers.origin) {
		res.setHeader('access-control-allow-origin', req.headers.origin);
		res.setHeader('access-control-allow-credentials', 'true');
	}
};

// set header for CORS
proxy.on("proxyRes", function(proxyRes, req, res) {
	enableCors(req, res);
});

// proxy.on('proxyRes', (proxyRes, req, res) => {
//   let allowedOrigin = false;
//   console.log('here...');
//   if (req.headers.origin) {
//     console.log('req.headers.origin: ',req.headers.origin);
//     const originHostName = url.parse(req.headers.origin).hostname;
//     console.log('originHostName: ',originHostName);
//     if (originHostName && allowedOrigins.some(o => o === originHostName)) {
//       res.setHeader('access-control-allow-origin', req.headers.origin);
//       res.setHeader('access-control-allow-credentials', 'true');
//       allowedOrigin = true;
//     }
//   }
//
//   if (req.headers['access-control-request-method']) {
//     res.setHeader('access-control-allow-methods', req.headers['access-control-request-method']);
//   }
//
//   if (req.headers['access-control-request-headers']) {
//     res.setHeader('access-control-allow-headers', req.headers['access-control-request-headers']);
//   }
//
//   if (allowedOrigin) {
//     console.log('req.method: ',req.method);
//     res.setHeader('access-control-max-age', 60 * 60 * 24 * 30);
//     if (req.method === 'OPTIONS') {
//       res.writeHead(200, { 'Content-Type': 'text/plain' });
//       res.end();
//     }
//   }
// });

// Create http server that leverages reverse proxy instance
// and proxy rules to proxy requests to different targets
http.createServer(function(req, res) {

  console.log('request his server...');

  if (req.method === 'OPTIONS') {
		enableCors(req, res);
		res.writeHead(200);
		res.end();
		return;
	}

  var client = jwksClient({
    jwksUri: 'http://is4:5000/.well-known/openid-configuration/jwks'
  });
  function getKey(header, callback){
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
    token = req.headers.authorization.substring(7, req.headers.authorization.length);
  } catch {
    res.writeHead(400, { 'Content-Type': 'text/plain' });
    return res.end();
  }

  jwt.verify(token, getKey, function(err, decoded) {
    if (err) {
      console.error(err);
      res.writeHead(401, { 'Content-Type': 'text/plain' });
      return res.end();
    }

    const target = proxyRules.match(req);

    if (target) {
      console.log('about to proxy to target')
      return proxy.web(req, res, {
        target: target
      }, function(err) {
        sendError(res, err);
      });
    }

    res.writeHead(400, { 'Content-Type': 'text/plain' });
    return res.end('The request url and path did not match any of the listed rules.');
  });






  //check for favicon GET ?
  //
  // if (req.url != '/favicon.ico') {
  //
  // }
  // a match method is exposed on the proxy rules instance
  // to test a request to see if it matches against one of the specified rules

  // var token;
  //
  // if (req.headers.authorization.startsWith("Bearer ")){
  //    token = req.headers.authorization.substring(7, req.headers.authorization.length);
  // } else {
  //    //Error
  //    res.writeHead(400, { 'Content-Type': 'text/plain' });
  //    res.end('Problem requesting...');
  // }
  //
  // console.log('req.url: ',req.url);
  // console.log('req.headers: ',req.headers);
  //
  // const username_password = 'api1:secret';
  // // const creds = btoa(username_password);
  // const creds = Buffer.from(username_password).toString('base64')

  // request({
  //   method: 'POST',
  //   uri: 'http://localhost:5000/connect/introspect',
  //   headers: {
  //     'Authorization': `Basic ${creds}`
  //   },
  //   form: {
  //     token: token
  //   }
  // }, function (err, response, body) {
  //   if (err) {
  //     res.writeHead(500, { 'Content-Type': 'text/plain' });
  //     res.end('Problem requesting...');
  //   }
  //   console.log('body: ',body);
    // if(response.statusCode == 201){
    //   console.log('document saved as: http://mikeal.iriscouch.com/testjs/'+ rand)
    // } else {
    //   console.log('error: '+ response.statusCode)
    //   console.log(body)
    // }
    // var target = proxyRules.match(req);
    // console.log('target: ',target);
    // if (target) {
    //   return proxy.web(req, res, {
    //     target: target
    //   });
    // }
    //
    // res.writeHead(500, { 'Content-Type': 'text/plain' });
    // res.end('The request url and path did not match any of the listed rules!');
  // });
}).listen(6010);

// http.createServer(function (req, res) {
//   res.writeHead(200, { 'Content-Type': 'text/plain' });
//   res.write('request successfully proxied to: ' + req.url + '\n' + JSON.stringify(req.headers, true, 2));
//   res.end();
// }).listen(8080);
