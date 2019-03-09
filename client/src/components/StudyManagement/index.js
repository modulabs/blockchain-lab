import React, { Component } from "react";
// import SimpleStorageContract from "./contracts/SimpleStorage.json";
import StudyContract from "../../contracts/Study.json"
import getWeb3 from "../../utils/getWeb3";

import "./index.css";

class StudyManagement extends Component {
  state = { storageValue: 0, web3: null, accounts: null, contract: null };

  componentDidMount = async () => {
    try {
      // Get network provider and web3 instance.
      const web3 = await getWeb3();

      // Use web3 to get the user's accounts.
      const accounts = await web3.eth.getAccounts();

      // Get the contract instance.
      const networkId = await web3.eth.net.getId();
      const deployedNetwork = StudyContract.networks[networkId];
      const instance = new web3.eth.Contract(
        StudyContract.abi,
        deployedNetwork && deployedNetwork.address,
      );

      // Set web3, accounts, and contract to the state, and then proceed with an
      // example of interacting with the contract's methods.
      this.setState({ web3, accounts, contract: instance }, this.runExample);
    } catch (error) {
      // Catch any errors for any of the above operations.
      alert(
        `Failed to load web3, accounts, or contract. Check console for details.`,
      );
      console.error(error);
    }
  };

  runExample = async () => {
    const { accounts, contract } = this.state;

    // Stores a given value, "Admin" by default.
    contract.methods.setAdmin("Admin").send({ from: accounts[0] });
    // contract.methods.setMember("member").send({ from: accounts[0] });
    // contract.methods.setSyllabus("0x01").send({ from: accounts[0] });

    // Get the value from the contract to prove it worked.
    const adminResponse = await contract.methods.getAdmin().call();
    // const memberResponse = await contract.methods.getMembers().call();
    // const syllabusResponse = await contract.methods.getSyllabus().call();

    // Update state with the result.
    this.setState({ adminName: adminResponse });
    // this.setState({ members: memberResponse });
    // this.setState({ syllabus: syllabusResponse });
  };

  render() {
    if (!this.state.web3) {
      return <div>Loading Web3, accounts, and contract...</div>;
    }
    return (
      <div className="StudyManagement">
        <h1>Study Smart Contract, Wed_blockchain</h1>
        <p>We are on the right track.</p>
        <h2>Study contract members</h2>
        <p>
          If your contracts compiled and migrated successfully, below will show
          the admin "admin" (by default).
        </p>
        <p>
          Try changing the value stored on <strong>line 40</strong> of App.js.
        </p>
        <div>The Admin is: {this.state.adminName }</div>
        <div>The members are: {this.state.members }</div>
        <div>The syllabus are: {this.state.syllabus }</div>
      </div>
    );
  }
}

export default StudyManagement;
