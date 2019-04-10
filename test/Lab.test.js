const Lab = artifacts.require("./Lab.sol");
const web3Utils = require("web3-utils");

contract("Lab", (accounts) => {
  let lab;
  const _labName = "wednesdayParty";

  beforeEach(async function() {
    lab = await Lab.new({ from: accounts[0] });
    await lab.setLabName("wednesdayParty", { from: accounts[0] });
  });

  it("assigns contract owner to the creator", async () => {
    const labOwner = await lab._labOwner();
    assert.equal(labOwner, accounts[0], "labOwner is not same with accounts[0].");
  });
  
  it("has a name", async () => {
    const labName = await lab.labName();
    assert.equal(labName, _labName, "labName is not set exactly.");
  });

  it("create Study(1)", async () => {
    await lab.createStudy("first study", 
      web3Utils.fromUtf8("noname0"), 
      web3Utils.fromUtf8("noname0@gmail.com"), 
      web3Utils.fromUtf8("https://noname0.github.io")
    );
    const count = await lab.getStudyCount();
    assert.equal(count, 1, "StudyList count is different.");
  });

  it("create Study(2)", async () => {
    await lab.createStudy("first study", 
      web3Utils.fromUtf8("noname0"), 
      web3Utils.fromUtf8("noname0@gmail.com"), 
      web3Utils.fromUtf8("https://noname0.github.io")
    );
    await lab.createStudy("second study", 
      web3Utils.fromUtf8("noname1"), 
      web3Utils.fromUtf8("noname1@gmail.com"), 
      web3Utils.fromUtf8("https://noname1.github.io")
    );
    const count = await lab.getStudyCount();
    assert.equal(count, 2, "StudyList count is different.");
  });

  it("create Study(3)", async () => {
    await lab.createStudy("first study", 
      web3Utils.fromUtf8("noname0"), 
      web3Utils.fromUtf8("noname0@gmail.com"), 
      web3Utils.fromUtf8("https://noname0.github.io")
    );
    await lab.createStudy("second study", 
      web3Utils.fromUtf8("noname1"), 
      web3Utils.fromUtf8("noname1@gmail.com"), 
      web3Utils.fromUtf8("https://noname1.github.io")
    );
    await lab.createStudy("third study", 
      web3Utils.fromUtf8("noname2"), 
      web3Utils.fromUtf8("noname2@gmail.com"), 
      web3Utils.fromUtf8("https://noname2.github.io")
    );
    const count = await lab.getStudyCount();
    assert.equal(count, 3, "StudyList count is different.");
  });
});