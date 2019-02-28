pragma solidity ^0.5.0;

contract Study {
  string lab_admin;

  function setAdmin(string memory s) public {
    lab_admin = s;
  }

  function getAdmin() public view returns(string memory) {
    return lab_admin;
  }
}