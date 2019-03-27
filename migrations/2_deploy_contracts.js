var Lab = artifacts.require("./Lab.sol")

module.exports = function(deployer) {
  // Class defined with Lectures when created
  // Class name, Lecture list
  deployer.deploy(Lab);
};