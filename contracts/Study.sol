pragma solidity ^0.5.0;

contract Study {
  string labAdmin;
  uint numOfStudent = 2; // hardcoded for now
  bytes8[] memberList = new bytes8[](numOfStudent); // init list

  function setAdmin(string memory s) public {
    labAdmin = s;
  }

  function getAdmin() public view returns(string memory) {
    return labAdmin;
  }

  function setMember(bytes8 member) public {
    memberList.push(member);
  }

  function getMembers() public returns(bytes8[] memory) {
    return memberList;
  }
}