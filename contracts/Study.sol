pragma solidity ^0.5.0;

contract Study {

  struct Student {
    bytes32 name;
    bytes32 email;
  }

  struct Admin {
    bytes32 name;
    bytes32 email;
  }

  struct Lecture {
    bytes32 lectureName;
    mapping(uint => address) attendee;
    uint attendeeSize;
  }

  struct Lab {
    address adminAddr;
    mapping(uint => Lecture) lectures;
    uint lecturesSize;
  }
  
  modifier onlyLabAdmin(bytes32 labName) {
    require(msg.sender == labs[labName].adminAddr, "Only Lab Admin can call this function!");
    _;
  }

  modifier onlyOwner() {
    require(msg.sender == contractOwner, "Only contract owner can call this function!");
    _;
  }

  mapping(address => Student) public students;
  mapping(address => Admin) public admins;
  mapping(bytes32 => Lab) public labs;
  bytes32[] labNames;

  address payable contractOwner;

  constructor() public {
    contractOwner = msg.sender;
  }

  function setAdmin(bytes32 name, bytes32 email) public {
    admins[msg.sender] = Admin(name, email);
  }

  function getAdmin(address addr) public view returns(bytes32, bytes32) {
    Admin memory admin = admins[addr];
    return (admin.name, admin.email);
  }

  function getLabAdmin(bytes32 labName) public view returns(bytes32, bytes32) {
    address addr = labs[labName].adminAddr;
    Admin memory admin = admins[addr];
    return (admin.name, admin.email);
  }

  function createLab(bytes32 labName) public {
    labs[labName] = Lab({
      adminAddr: msg.sender,
      lecturesSize: 0
    });
    labNames.push(labName);
  }

  function setLab(bytes32 labName, bytes32[] memory lectureNames) public {
    labs[labName].lecturesSize = lectureNames.length;
    for (uint i = 0; i < lectureNames.length; i++) {
      labs[labName].lectures[i] = Lecture({
        lectureName: lectureNames[i],
        attendeeSize: 0
      });
    }
  }

  function kill() public onlyOwner {
    selfdestruct(contractOwner);
  }

  function setStudent(bytes32 name, bytes32 email) public {
    students[msg.sender] = Student(name, email);
  }

  function getStudent(address st) public view returns (bytes32, bytes32) {
    require(msg.sender == st || msg.sender == contractOwner);
    return (students[st].name, students[st].email);
  }

  function getLectures(bytes32 labName) public view returns (bytes32[] memory lectureList) {
    lectureList = new bytes32[](labs[labName].lecturesSize);
    for (uint i = 0; i < labs[labName].lecturesSize; i++) {
      lectureList[i] = labs[labName].lectures[i].lectureName;
    }
  }

  function setAttendance(bytes32 labName, uint lectureNum) public {
    labs[labName].lectures[lectureNum].attendee[labs[labName].lectures[lectureNum].attendeeSize] = msg.sender;
    labs[labName].lectures[lectureNum].attendeeSize += 1;
  }

  function getAttendance(bytes32 labName, uint lectureNum) public view returns (address[] memory attendeeList) {
    attendeeList = new address[](labs[labName].lectures[lectureNum].attendeeSize);
    for (uint i = 0; i < labs[labName].lectures[lectureNum].attendeeSize; i++) {
      attendeeList[i] = labs[labName].lectures[lectureNum].attendee[i];
    }
  }
}
