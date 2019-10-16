index = require("./index")

req = {
  query: {
    dry_run: 'false',
    limit: 1
  }
}

class Response {
  constructor() {}

  status(code) {
    console.log(code)
    return this
  }

  send(text) {
    console.log(text)
    return this
  }
}
res = new Response();

index.helloWorld(req, res)
