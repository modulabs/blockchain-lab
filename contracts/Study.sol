pragma solidity ^0.5.0;

contract Study {

    struct Student {
        bytes32 name;
        bytes32 email;
    }

    struct Lecture {
        bytes32 lectureName;
        address[] attandee;
    }

    address studyAdmin;
    string studyName;
    mapping(address => Student) public students;
    Lecture[] class;

    constructor() public {
        studyAdmin = msg.sender;

    }

    function setLecture(bytes32[] memory lectureNames) public {
        require(msg.sender == studyAdmin);
        for(uint i=0; i<lectureNames.length; i++) {
            class.push(Lecture({
                lectureName: lectureNames[i],
                attandee: new address[](0)
            }));
        }
    }

    function setStudyName(string memory _studyName) public {
        studyName = _studyName;
    }

    function kill() public{
        require(msg.sender == studyAdmin);
        selfdestruct(msg.sender);
    }

    function getAdmin() public view returns(address) {
        return studyAdmin;
    }

    function setStudent(bytes32 name, bytes32 email) public{
        students[msg.sender] = Student(name, email);
    }

    function getStudent(address st) public view returns(bytes32, bytes32) {
        require(msg.sender == st || msg.sender == studyAdmin);
        return (students[st].name, students[st].email);
    }

    function getLectures() public view returns (bytes32[] memory lectureList) {
        lectureList = new bytes32[](class.length);
        for(uint i=0; i<class.length; i++) {
            lectureList[i] = class[i].lectureName;
        }
    }
    function setAttendance(uint lectureNum) public {
        class[lectureNum].attandee.push(msg.sender);
    }

    function getAttendance(uint lectureNum) public view returns (address[] memory){
        return class[lectureNum].attandee;
    }
}
