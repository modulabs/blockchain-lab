import React, { Component } from "react";
// import SimpleStorageContract from "./contracts/SimpleStorage.json";
import StudyContract from "../../contracts/Study.json"
import getWeb3 from "../../utils/getWeb3";

import "./index.css";

class MyStudy extends Component {
  state = { storageValue: 0, web3: null, accounts: null, contracts: [], selected: 0 };

  componentDidMount = async () => {
    try {
      // Get network provider and web3 instance.
      const web3 = await getWeb3();

      // Use web3 to get the user's accounts.
      const accounts = await web3.eth.getAccounts();

      // Get the contract instance.
      const contractAddress = window.location.search.split("=")[1];
      
      const studyInstance = new web3.eth.Contract(
        StudyContract.abi,
        contractAddress,
      );
      const studyName = await studyInstance.methods.getStudyName().call();
      const adminName = await studyInstance.methods.getOwner().call();
      const syllabusURL = web3.utils.toUtf8(await studyInstance.methods.getSyllabus().call());
      const sessionNumber = (await studyInstance.methods.getSessionNumber().call()).toNumber();
      const attendances = [];
      for(let i = 0; i < sessionNumber; i++) {
        attendances[i] = await studyInstance.methods.getAttendance(i).call();
      }
      console.log(attendances);
      this.setState({ web3, accounts, contract: studyInstance, studyName, adminName, syllabusURL, sessionNumber, attendances });
      // Set web3, accounts, and contract to the state, and then proceed with an
      // example of interacting with the contract's methods.
      //
    } catch (error) {
      // Catch any errors for any of the above operations.
      alert(
        `Failed to load web3, accounts, or contract. Check console for details.`,
      );
      console.error(error);
    }
  };

  runExample = async () => {
    const { accounts, contracts } = this.state;
    if(this.state.selected >= this.state.contracts.length - 1 && this.state.selected !== 0) {
      this.setState({ selected: 0 }, this.runExample);
      return;
    }
    if(this.state.contracts.length === 0) return;
    const contract = contracts[this.state.selected];
    // Get the value from the contract to prove it worked.
    const adminResponse = await contract.methods.getOwner().call();

    // Update state with the result.
    this.setState({ adminName: adminResponse });
    // register new student informaion
    contract.methods.setStudent(this.state.web3.utils.utf8ToHex("name",32),
                                this.state.web3.utils.utf8ToHex("test@modulabs.com",32)).send({ from: accounts[0] });
    const stu_resp = await contract.methods.getStudent(accounts[0]).call();
    this.setState({ stu_n: stu_resp[0], stu_e: stu_resp[1] });

    // get lecture list
    const lec_resp = await contract.methods.getLectures().call();
    this.setState({ lec: lec_resp });
    
    // set attendee to lectures
    // lecture0
    contract.methods.setAttendance(0).send({ from: accounts[0] });
    contract.methods.setAttendance(0).send({ from: accounts[1] });
    contract.methods.setAttendance(0).send({ from: accounts[2] });
    // lecture1
    contract.methods.setAttendance(1).send({ from: accounts[3] });
    contract.methods.setAttendance(1).send({ from: accounts[4] });

    // get attendee
    const lec0_att = await contract.methods.getAttendance(0).call();
    const lec1_att = await contract.methods.getAttendance(1).call();
    this.setState({ lec0: lec0_att });
    this.setState({ lec1: lec1_att });
    
  };

  render() {
    if (!this.state.web3) {
      return <div>Loading Web3, accounts, and contract...</div>;
    }
    return (
      <div className="MyStudy">
        <h1>Study Smart Contract, { this.state.studyName }</h1>
        <p>We are on the right track.</p>
        <h2>Study contract members</h2>
        <p>
          If your contracts compiled and migrated successfully, below will show
          the admin "admin" (by default).
        </p>
        <p>
          Try changing the value stored on <strong>line 40</strong> of App.js.
        </p>
        <div>The Admin is: { this.state.adminName }</div>
        <div>The number of lectures is: {this.state.sessionNumber }</div>
        <div>You can find information of study at <a href={this.state.syllabusURL}>here</a></div>
        {
          this.state.attendances.map((attendance, key) => {
            return <div>
              The lecture{ key } attandance are: { attendance }
            </div>;
          })
        }
      </div>
    );
  }
}

export default MyStudy;
