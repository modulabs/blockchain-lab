const Study = artifacts.require("./Study.sol");

contract("Study", accounts => {
  it("test Study.", async () => {
    // const StudyInstance = await Study.deployed();

    /*
    // Set value of Admin
    await StudyInstance.setAdmin(web3.utils.fromAscii("Admin"), web3.utils.fromAscii("admin@modulabs.co.kr"), { from: accounts[0] });

    // Get stored value
    const storedData = await StudyInstance.getAdmin.call(accounts[0]);
    assert.equal(web3.utils.toAscii(storedData[0]).replace(/\0/g, ''), "Admin", "The value name was not stored.");
    assert.equal(web3.utils.toAscii(storedData[1]).replace(/\0/g, ''), "admin@modulabs.co.kr", "The value email was not stored.");
    */
  });
});