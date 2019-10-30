const rp = require('request-promise');

const ASSETS = '/assets';
const TRADING_PAIRS = '/trading-pairs';

const host = 'api.gopax.co.kr';

const assetsOption = {
  method: 'GET',
  json: true,
  url: `https://${host}${ASSETS}`,
};

const tradingOption = {
  method: 'GET',
  json: true,
  uri: `https://${host}${TRADING_PAIRS}`,
};

function requestWithOption(option) {
  return rp(option).then((response) => {
    let filtered = response.filter((elem) => elem.name.slice(4, 7) === 'KRW');
    return filtered;
  }).catch((err) => {
    console.log(err);
    return;
  });
}

// requestWithOption(assetsOption);
requestWithOption(tradingOption).then((pairs) => {
  console.log(pairs, pairs.length);
});