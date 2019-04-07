const Lab = artifacts.require("./Lab.sol");

contract("Lab", accounts => {
  it("test Lab.", async () => {
    const LabInstance = await Lab.deployed();

    // Set value of labName
    await LabInstance.setLabName("wednesdayParty", { from: accounts[0] });

    // Get stored value
    const storedData = await LabInstance.labName.call();
    assert.equal(storedData, "wednesdayParty", "The value name was not stored.");
  });
});