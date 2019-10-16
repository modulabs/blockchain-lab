pragma solidity ^0.5.0;

import "truffle/Assert.sol";
import "truffle/DeployedAddresses.sol";
import "../contracts/Study.sol";

contract TestStudy {
  function testItStoresAValue() public {
    // Study study = Study(DeployedAddresses.Study());

    /*
    study.setAdmin("Admin");

    string memory expected = "Admin";

    Assert.equal(study.getAdmin(), expected, "It should store the value admin.");
    */
  }
}
