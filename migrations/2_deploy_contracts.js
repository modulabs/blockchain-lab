// var SimpleStorage = artifacts.require("./SimpleStorage.sol");
var Study = artifacts.require("./Study.sol");

module.exports = function(deployer) {
  // deployer.deploy(SimpleStorage);
  deployer.deploy(Study)
};