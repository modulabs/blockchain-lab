pragma solidity ^0.5.0;

contract Study {

    struct Student {
        bytes32 name;
        bytes32 email;
        bool isAdmin;
    }

    struct Session {
        bytes32 sessionName;
        bytes32 materialURL;
        address[] attandeeList;
    }

    address payable studyOwner;
    string studyName;
    bytes32 syllabusURL;
    
    mapping(address => Student) public students;
    mapping(uint => Session) public sessions;
    uint sessionNumber;

    // modifier for admin
    modifier onlyAdmin() {
        require(students[msg.sender].isAdmin, "Only study admin can call this function!");
        _;
    }
    // modifier for owner
    modifier onlyOwner() {
        require(msg.sender == studyOwner, "Only study owner can call this function!");
        _;
    }

    // events
    event StudyStateChange(string _studyName, bytes32 _syllabusURL, string message);
    event MemberStateChange(address member,string message);

    constructor(string memory _studyName, bytes32 _ownerName, bytes32 _ownerEmail, bytes32 _syllabusURL) public {
        studyName = _studyName;
        studyOwner = msg.sender;
        students[studyOwner] = Student(_ownerName, _ownerEmail, true);
        syllabusURL = _syllabusURL;
        sessionNumber = 1;
        emit StudyStateChange(_studyName, _syllabusURL, "Study Created");
    }

    // Functions for set or get member state of Study
    function setStudent(bytes32 _name, bytes32 _email, address _candidate) public onlyAdmin{
        students[_candidate] = Student(_name, _email, false);
        emit MemberStateChange(_candidate, "New student added.");
    }

    function getStudentInfo(address _student) public view returns (bytes32, bytes32) {
        require(msg.sender == _student || students[msg.sender].isAdmin);
        return (students[_student].name, students[_student].email);
    }

    function setAdmin(address _candidate) public onlyOwner{
        // require(students[_candidate] != 0, "This address is not student.");
        students[_candidate].isAdmin = true;
        emit MemberStateChange(_candidate, "New admin assigned.");
    }

    function getOwner() public view returns(address) {
        return studyOwner;
    }

    // Functions for sessions in study
    function AddSession(bytes32 _sessionName, bytes32 _materialURL) public onlyAdmin{
        Session memory newSession = Session({
            sessionName: _sessionName,
            materialURL: _materialURL,
            attandeeList: new address[](0)
        }); // Have to check that newsession is not disappeared after func. AddSession is ended.
        sessions[sessionNumber] = newSession;
        sessionNumber++;
    }

    // function getSessionInfo(uint _sessionNumber) public view returns (Session memory) {
    //     // require(sessions[_sessionNumber] != 0, "This session is not set yet.");
    //     return sessions[_sessionNumber];
    //   }

    // function setAttendance(uint _sessionNumber, address _attendee) public onlyAdmin {
    //     // require(sessions[_sessionNumber] != 0, "This session is not set yet.");
    //     sessions[_sessionNumber].attendeeList.push(_attendee);
    // }

    // function getAttendance(uint _sessionNumber) public view returns (address[] memory attendeeList) {
    //     // require(sessions[_sessionNumber] != 0, "This session is not set yet.");
    //     return sessions[_sessionNumber].attendeeList;    
    //   }

    // Functions for changing study states
    function changeStudyName(string memory _studyName) public onlyOwner{
        studyName = _studyName;
        emit StudyStateChange(_studyName, syllabusURL, "Study name changed");
    }

    function changeSyllabusURL(bytes32 _syllabusURL) public onlyOwner{
        syllabusURL = _syllabusURL;
        emit StudyStateChange(studyName, _syllabusURL, "Syllabus URL changed");
    }
    function kill() public onlyOwner{
        selfdestruct(msg.sender);
    }

    

    
}   
