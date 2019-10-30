const crypto = require('crypto');
const request = require('request');

// 발급받은 api키와 시크릿키를 입력한다
const apikey = '';
const secret = '';

const method = 'GET';
const requestPath = '/assets';

const host = 'api.gopax.co.kr';

var options = {
  method,
  json: true,
  url: `https://${host}${requestPath}`,
  /*
  headers: {   // Not for now.
    'API-KEY': apikey,
    Signature: sign,
    Nonce: nonce,
  },
  */
  strictSSL: false,
};

request(options, (err, response, b) => {
  if (err) {
    console.log('err:', err);
    return;
  }
  console.log(b);
});