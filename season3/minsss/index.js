const request = require('request');

const method = 'GET';

const ASSETS = '/assets';
const TRADING_PAIRS = '/trading-pairs';

const host = 'api.gopax.co.kr';

const assetsOption = {
  method,
  json: true,
  url: `https://${host}${ASSETS}`,
  strictSSL: false,
};

const tradingOption = {
  method,
  json: true,
  url: `https://${host}${TRADING_PAIRS}`,
  strictSSL: false,
};

function requestWithOption(option) {
  request(option, (err, response, b) => {
    if (err) {
      console.log('err:', err);
      return;
    }
    console.log(b);
  });
}

requestWithOption(assetsOption);
requestWithOption(tradingOption);