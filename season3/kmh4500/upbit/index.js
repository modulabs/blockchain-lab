const dotenv = require('dotenv');
dotenv.config();
const accessKey = process.env.ACCESS_KEY
const secretKey = process.env.SECRET_KEY
const server_url = "https://api.upbit.com"

var request = require("request");
const uuidv4 = require("uuid/v4")
const crypto = require('crypto')
const sign = require("jsonwebtoken").sign
const queryEncode = require("querystring").encode
const budget = 100000
var rp = require('request-promise');

async function get_price(market) {
  var options = { method: 'GET',
  url: 'https://api.upbit.com/v1/candles/minutes/1',
  json: true,
  qs: { market: market } };

  return rp(options).then((body) => {
    // if (error) throw new Error(error);
    console.log(body);
    console.log(body[0]['trade_price'])
    return body[0]['trade_price']
  }).catch(function (err) {
    console.log(err)
  });
}

function buy(price, volume, market) {
  order('bid', price, volume, market)
}

function sell(price, volume, market) {
  order('ask', price, volume, market)
}

function order(side, price, volume, market) {
  const ord_type = 'limit'
  const body = {market: market, side: side, volume: volume, price: price, ord_type: ord_type};
  const payload = {
    access_key: accessKey,
    nonce: (new Date).getTime(),
    query: queryEncode(body)
  };
  const token = sign(payload, secretKey);

  var options = {
    method: "POST",
    url: "https://api.upbit.com/v1/orders",
    headers: {Authorization: `Bearer ${token}`},
    json: body
  };

  return rp(options).then((body) => {
    console.log(body);
    return body;
  });
}

function get_orders() {

  const payload = {
      access_key: accessKey,
      nonce: uuidv4(),
  }

  const token = sign(payload, secretKey)

  const options = {
      method: "GET",
      url: server_url + "/v1/orders",
      headers: {Authorization: `Bearer ${token}`},
      json: true
  }

  return rp(options).then((body) => {
    console.log(body);
    return body;
  });
}

function get_balance() {
  const payload = {
      access_key: accessKey,
      nonce: uuidv4(),
  }

  const token = sign(payload, secretKey)

  const options = {
      method: "GET",
      url: "https://api.upbit.com/v1/accounts",
      headers: {Authorization: `Bearer ${token}`},
      json: true
  }

  return rp(options).then((body) => {
    console.log(body);
    return body;
  });
}

function cancel_order(uuid) {
  const body = {
      uuid: uuid
  }

  const query = queryEncode(body)

  const hash = crypto.createHash('sha512')
  const queryHash = hash.update(query, 'utf-8').digest('hex')

  const payload = {
      access_key: accessKey,
      nonce: uuidv4(),
      query_hash: queryHash,
      query_hash_alg: 'SHA512',
  }

  const token = sign(payload, secretKey)

  const options = {
      method: "DELETE",
      url: server_url + "/v1/order?" + query,
      headers: {Authorization: `Bearer ${token}`},
      json: body
  }

  return rp(options).then((body) => {
    console.log(body);
    return body;
  });
}
const prev_price = 183900
var volume_sum = 0
var spent = 0
var earn_sum = 0
async function main(dry_run = True) {
  orders = await get_orders()
  console.log(orders)
  for (const order of orders) {
    await cancel_order(order.uuid)
  }

  eth_price = await get_price('KRW-ETH')
  btc_price = await get_price('KRW-BTC')
  balance = await get_balance()
  btc_balance = -1
  eth_balance = -1
  krw_balance = -1
  console.log(typeof balance)
  balance.forEach((item) => {
    if (item["currency"] === 'BTC') {
      btc_balance = Number(item["balance"])
    }
    if (item["currency"] === 'ETH') {
      eth_balance = Number(item["balance"])
    }
    if (item["currency"] === 'KRW') {
      krw_balance = Number(item["balance"])
    }
  })
  console.log(btc_balance, eth_balance, krw_balance)
  console.log(btc_price, eth_price)
  if (btc_balance == -1 || eth_balance == -1 || krw_balance == -1) {
    return "balance error"
  }
  console.log(typeof eth_balance)
  total = btc_balance * btc_price + eth_balance * eth_price + krw_balance
  console.log('total', total)
  each = total / 3
  coins = [{balance: btc_balance, price: btc_price, market: 'KRW-BTC'},
           {balance: eth_balance, price: eth_price, market: 'KRW-ETH'}]
  console.log('each', each)
  for (const item of coins) {
    diff = item.balance * item.price - each
    amount = Math.abs(diff / item.price)
    thresh = each * 0.01
    console.log(item.market, 'diff', diff, 'thresh', thresh, 'price', item.price, 'amount', amount)
    if (!dry_run && diff < -thresh) {
      console.log('buy')
      await buy(item.price, amount, item.market)
    } else if (diff > thresh) {
      console.log('sell')
      await sell(item.price, amount, item.market)
    }
  }
}

exports.helloWorld = (req, res) => {
  dry_run = true
  console.log("req.query.dry_run", req.query.dry_run)
  if (req && req.query && req.query.dry_run === 'false') {
    dry_run = false
  }
  console.log("dry_run", dry_run)
	return main(dry_run).then(
    text => {
      res.status(200).send(text);
    },
    err => {
      res.status(200).send(err);
    }
	);
};
/*
const request = require("request")
const sign = require("jsonwebtoken").sign
const queryEncode = require("querystring").encode

const query = queryEncode({state: state, page: 1});
const payload = {
  access_key: accessKey,
  nonce: (new Date).getTime(),
  query: query
};
const token = sign(payload, secretKey);

var options = {
  method: "GET",
  url: "https://api.upbit.com/v1/orders?" + query,
  headers: {Authorization: `Bearer ${token}`}
};

request(options, function (error, response, body) {
  if (error) throw new Error(error);
  console.log(body);
});
*/
