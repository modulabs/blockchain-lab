const Study = artifacts.require("./Study.sol");

contract("Study", accounts => {
  it("test Study.", async () => {
    const StudyInstance = await Study.deployed();

    // Set value of Admin
    await StudyInstance.setAdmin("Admin", { from: accounts[0] });

    // Get stored value
    const storedData = await StudyInstance.get.call();

    assert.equal(storedData, "admin", "The value Admin was not stored.");
  });
});
