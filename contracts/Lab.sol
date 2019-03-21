pragma solidity ^0.5.0;

import "./Study.sol";

contract Lab {
    address public _labOwner;
    string public labName;
    address[] public studyList;

    event StudyCreated(address studyAddr, address studyAdmin);

    constructor () public {
        _labOwner = msg.sender;
    }

    function setLabName (string memory _labName) public {
        require(msg.sender == _labOwner);
        labName = _labName;
    }

    function createStudy(
        string memory _studyName, 
        bytes32 _ownerName, 
        bytes32 _ownerEmail,
        bytes32 _syllabusURL) 
        public returns (bool)
        {
        Study newStudy = new Study(_studyName, _ownerName, _ownerEmail, _syllabusURL);
        address _addr = address(newStudy);
        studyList.push(_addr);
        emit StudyCreated(_addr, msg.sender);
        return true;
    }
}
