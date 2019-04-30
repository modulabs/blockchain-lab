pragma solidity ^0.5.0;

/// @author The Modulabs Team
/// @title A Study contract

contract Study {

    struct Student {
        bytes32 name;
        bytes32 email;
        bool isStudent;
        bool isAdmin;
    }

    struct Session {
        bytes32 sessionName;
        bytes32 materialURL;
        address[] attendeeList;
    }

    enum MemberState { StudentAssigned, StudentRemoved, AdminAssigned, AdminRemoved }

    address payable studyOwner;
    string studyName;
    bytes32 syllabusURL;
    
    mapping(address => Student) students;
    mapping(uint => Session) sessions;
    uint studentNumber;
    uint sessionNumber;

    /// modifier for admin
    modifier onlyAdmin() {
        require(students[msg.sender].isAdmin, "Only study admin can call this function!");
        _;
    }

    /// modifier for owner
    modifier onlyOwner() {
        require(msg.sender == studyOwner, "Only study owner can call this function!");
        _;
    }

    /// events
    event StudyStateChange(string _studyName, bytes32 _syllabusURL, string message);
    /**
     * @dev event MemberStateChange
     * @notice parameter memberState = {0: StudentAssigned, 1: StudentRemoved, 2: AdminAssigned, 3:AdminRemoved}
     */
    event MemberStateChange(address indexed member, int8 indexed memberState);
    event OwnershipTransferred(address indexed previousOwner, address indexed newOwner);

    /**
     * @dev Constructor of Study Contract, sets basic information of the _studyOwner in Student struct.
     * @param _studyOwner Who called createStudy method in Lab contract
     * @param _studyName Name of the study
     * @param _ownerName ,@param _ownerEmail : Owner Info
     * @param _syllabusURL URL to the documentation that describes this study
     * @notice sessionNumber is initialized to 1. the zeroth session might be special session (e.g. Orientation)
     * that can be set by study owner.
     * @notice Study owner is the study owner by default.
     */
    constructor(address payable _studyOwner, string memory _studyName, bytes32 _ownerName, bytes32 _ownerEmail, bytes32 _syllabusURL) public {
        studyName = _studyName;
        studyOwner = _studyOwner;
        students[studyOwner] = Student(_ownerName, _ownerEmail, true, true);
        syllabusURL = _syllabusURL;
        sessionNumber = 0;
        studentNumber = 1;
        emit StudyStateChange(_studyName, _syllabusURL, "Study Created");
    }

    /**
     * @dev Simple Functions for extracting study information. 
     */
    function getStudyName() public view returns (string memory) {
        return studyName;
    }

    function getSyllabus() public view returns (bytes32) {
        return syllabusURL;
    }

    function getOwner() public view returns(address) {
        return studyOwner;
    }

    function getStudentNumber() public view returns(uint) {
        return studentNumber;
    }

    function getSessionNumber() public view returns(uint) {
        return sessionNumber;
    }

    /**
     * @dev Function for set student by adding Student struct to the students mapping.
     * only admin can set the student.
     * event emitted by the student addition.
     */
    function setStudent(bytes32 _name, bytes32 _email, address _candidate) public onlyAdmin {
        students[_candidate] = Student(_name, _email, true, false);
        emit MemberStateChange(_candidate, int8(MemberState.StudentAssigned));
        studentNumber++;
    }

    /**
     * @dev Function for remove student by changing Student struct in the students mapping.
     * only admin can remove the student.
     * event emitted by the student addition.
     */
    function removeStudent(address _student) public onlyAdmin {
        require(students[_student].isStudent == true, "This address is not a student");
        require(students[_student].isAdmin == false, "Admin member can not be removed by other admin");
        students[_student] = Student(0, 0, false, false);
        emit MemberStateChange(_student, int8(MemberState.StudentRemoved));
        studentNumber--;
    }

    /**
     * @dev Function for extracting student's basic information.
     * only the student itself and admin can get the info.
     * @return student name and email in bytes32 type.
     */
    function getStudentInfo(address _student) public view returns (bytes32, bytes32, bool) {
        require(msg.sender == _student || students[msg.sender].isAdmin);
        return (students[_student].name, students[_student].email, students[_student].isAdmin);
    }

    /**
     * @dev Function for setting admin. This is can only be run by the studyOwner.
     * @notice There might be more than one admins.
     * @param _candidate is the admin candidate address which is required to be a student in advance.
     */
    function setAdmin(address _candidate) public onlyOwner {
        require(students[_candidate].isStudent, "This address is not student.");
        require(students[_candidate].isAdmin == false, "This address is already an admin.");
        students[_candidate].isAdmin = true;
        emit MemberStateChange(_candidate, int8(MemberState.AdminAssigned));
    }

    /**
     * @dev Function for removing admin. This is can only be run by the studyOwner.
     * @param _admin is the admin candidate address which is required to be an admin in advance.
     */
    function removeAdmin(address _admin) public onlyOwner {
        require(students[_admin].isStudent == true, "This address is not a student");
        require(students[_admin].isAdmin == true, "This address is not an admin.");
        students[_admin].isAdmin = false;
        emit MemberStateChange(_admin, int8(MemberState.AdminRemoved));
    }
    
    /**
     * @dev Function for add one session to the sessions mapping, only Admin can set it.
     * @param _sessionName : bytes32 type session name.
     * @param _materialURL : bytes32 type URL of session material.
     */
    function addSession(bytes32 _sessionName, bytes32 _materialURL) public onlyAdmin {
        Session memory newSession = Session({
            sessionName: _sessionName,
            materialURL: _materialURL,
            attendeeList: new address[](0)
        }); 
        sessions[sessionNumber] = newSession;
        sessionNumber++;
    }

    /**
     * @dev Function get basic session information.
     * @param _sessionNumber : the number of session we want to get information from.
     * @return basic session information(session Name, Session material URL) in bytes32 type.
     */
    function getSessionInfo(uint _sessionNumber) public view returns (bytes32, bytes32) {
        require(sessions[_sessionNumber].sessionName != 0, "This session is not set yet.");
        return (sessions[_sessionNumber].sessionName, sessions[_sessionNumber].materialURL);
    }

    /**
     * @dev Function for set attendance in the specific session.
     * @param _sessionNumber : the session we want to add attendance.
     * @param _attendee : the address who attended the session.
     * @notice Only admin can call this function and the attendee is required to be a student.
     * @notice new attendee added to the attendeeList in the Session.attendeeList.
     */
    function setAttendance(uint _sessionNumber, address _attendee) public onlyAdmin {
        require(sessions[_sessionNumber].sessionName != 0, "This session is not set yet.");
        require(students[_attendee].isStudent, "This address is not student.");
        sessions[_sessionNumber].attendeeList.push(_attendee);
    }

    /**
     * @dev Function for get attendance of specific session.
     * @param _sessionNumber specific session number that we want to know.
     * @return attendeeList of the session
     */
    function getAttendance(uint _sessionNumber) public view returns (address[] memory attendeeList) {
        require(sessions[_sessionNumber].sessionName != 0, "This session is not set yet.");
        return sessions[_sessionNumber].attendeeList;    
    }

    /**
     * @dev Function for changing studyName.
     * @param _studyName : new study name in string type.
     * @notice only Owner of the study can change the study name.
     * @notice event StudyStateChange emitted.
     */
    function changeStudyName(string memory _studyName) public onlyOwner {
        studyName = _studyName;
        emit StudyStateChange(_studyName, syllabusURL, "Study name changed");
    }

    /**
     * @dev Function for changing study syllabusURL.
     * @param _syllabusURL : new study syllabusURL in bytes32 type.
     * @notice only Owner of the study can change the study syllabusURL.
     * @notice event StudyStateChange emitted.
     */
    function changeSyllabusURL(bytes32 _syllabusURL) public onlyOwner {
        syllabusURL = _syllabusURL;
        emit StudyStateChange(studyName, _syllabusURL, "Syllabus URL changed");
    }

    /**
     * @dev Functions for ownership management.
     * @param newOwner The address to transfer ownership to.
     * @notice only Owner can call this function
     */
    function transferOwnership(address payable newOwner) public onlyOwner {
        _transferOwnership(newOwner);
    }

    /**
     * @dev Study destruction function
     * @notice only Owner can call this function
     */    
    function kill() public onlyOwner {
        selfdestruct(msg.sender);
    }  

    /**
     * @dev Helper functions for ownership management.
     * @param newOwner The address to transfer ownership to.
     * @notice check if the newOwner is the zero address, so that the ownership can be recovered.
     * @notice only Owner can call this function
     */
    function _transferOwnership(address payable newOwner) internal {
        require(newOwner != address(0));
        emit OwnershipTransferred(studyOwner, newOwner);
        studyOwner = newOwner;
    }
}   
