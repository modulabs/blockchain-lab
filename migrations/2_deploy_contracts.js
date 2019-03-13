// var SimpleStorage = artifacts.require("./SimpleStorage.sol");
var Study = artifacts.require("./Study.sol");

module.exports = function(deployer) {
  // Class defined with Lectures when created
  // Class name, Lecture list
  deployer.deploy(Study, "0x01", ["0x02","0x03"]);
};
