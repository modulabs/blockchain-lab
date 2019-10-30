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
  request(option, (err, response, data) => {
    if (err) {
      console.log('err:', err);
      return;
    }
    let filtered = data.filter((elem) => elem.name.slice(4, 7) === 'KRW');
    console.log(filtered);
  });
}

// requestWithOption(assetsOption);
requestWithOption(tradingOption);