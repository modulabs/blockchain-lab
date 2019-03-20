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

    function createStudy(string memory _studyName) public {
        Study newStudy = new Study();
        newStudy.setStudyName(_studyName);
        address _addr = address(newStudy);
        studyList.push(_addr);
        emit StudyCreated(_addr, msg.sender);
    }
}
