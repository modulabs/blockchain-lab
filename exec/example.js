const Lab = artifacts.require("./Lab.sol");

module.exports = async () => {
  let labContract = await Lab.deployed();
  web3.eth.getAccounts(function(err,res) { accounts = res; });


  await labContract.setLabName("blockchain lab", { from: accounts[0] });
  await labContract.createStudy("first study", web3.utils.fromUtf8("noname0"), web3.utils.fromUtf8("noname0@gmail.com"), web3.utils.fromUtf8("https://noname0.github.io"));
};

