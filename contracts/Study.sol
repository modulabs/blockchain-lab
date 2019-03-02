pragma solidity ^0.5.0;

contract Study {
  string labAdmin;

  function setAdmin(string memory s) public {
    labAdmin = s;
  }

  function getAdmin() public view returns(string memory) {
    return labAdmin;
  }
}