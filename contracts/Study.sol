pragma solidity ^0.5.0;

contract Study {
  string labAdmin;
  uint numOfStudent = 2; // hardcoded for now
  bytes8[] memberList = new bytes8[](numOfStudent); // init list
  uint numOfSylabus = 5;
  bytes4[] syllabusList = new bytes4[](numOfSylabus);

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

  function setSyllabus(bytes4 sylabus) public {
    syllabusList.push(sylabus);
  }

  function getSyllabus() public returns(bytes4[] memory) {
    return syllabusList;
  }
}