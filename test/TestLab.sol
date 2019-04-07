pragma solidity ^0.5.0;

import "truffle/Assert.sol";
import "truffle/DeployedAddresses.sol";
import "../contracts/Lab.sol";

contract TestLab {
  function testInitLabName() public {
    Lab labTest = Lab(DeployedAddresses.Lab());

    // labTest.setLabName("wednesdayParty");
    // string memory expected = "wednesdayParty";
    // Assert.equal(labTest.getLabName(), expected, "It should store the value wednesdayParty.");
  }
}
