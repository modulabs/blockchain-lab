import React, { Component } from "react";
import getWeb3 from "../../utils/getWeb3";
import LabContract from "../../contracts/Lab.json";
import "./index.scss";

class AddStudy extends Component {
  constructor(props) {
    super(props);
    this.state = {
    };

    this.handleInputChange = this.handleInputChange.bind(this);
    this.handleSubmit = this.handleSubmit.bind(this);
  }

  componentDidMount = async () => {

    const web3 = await getWeb3();
    const accounts = await web3.eth.getAccounts();

    this.setState({
      web3,
      ownerAddress: accounts[0]
    });
  }

  handleInputChange(event) {
    const target = event.target;
    const value = target.type === 'checkbox' ? target.checked : target.value;
    const name = target.name;
    this.setState({
      [name]: value
    });
  }

  handleSubmit = async (event) => { 
    event.preventDefault();
    if(this.state.studyName == void 0) {
      alert('Write Study Name!');
      return;
    }

    if(this.state.ownerName == void 0) {
      alert('Write Owner Name!');
      return;
    }

    if(this.state.ownerEmail == void 0) {
      alert('Write Owner Email!');
      return;
    }

    if(this.state.syllabusURL == void 0) {
      alert('Submit Study syllabus!');
      return;
    }

    const web3 = this.state.web3;
    const networkId = await web3.eth.net.getId();
    const deployedNetwork = LabContract.networks[networkId];
    const labInstance = new web3.eth.Contract(
      LabContract.abi,
      deployedNetwork && deployedNetwork.address,
    );
    labInstance.methods.createStudy(this.state.studyName, 
      web3.utils.padRight(web3.utils.fromAscii(this.state.ownerName), 64), 
      web3.utils.padRight(web3.utils.fromAscii(this.state.ownerEmail), 64), 
      web3.utils.padRight(web3.utils.fromAscii(this.state.syllabusURL), 64)
    ).send({ from: this.state.ownerAddress, gas: 6000000 }).on('transactionHash', hash => {
      //console.log(hash);
      alert(`transaction creation success: ${hash}`);
    }).on('confirmation', (confirmationNumber, receipt) => {
      console.log(confirmationNumber);
    }).on('receipt', receipt => {
      console.log(receipt);
    }).on('error', error => {
      alert(`transaction failed: ${error}`);
    });
  }

  render() {
    return (
      <form onSubmit={this.handleSubmit}>
        <label>
          Study Name:
          <input
            name="studyName"
            value={this.state.studyName}
            type="text"
            onChange={this.handleInputChange} />
        </label>
        <br />
        <label>
          Owner Address:
          <input
            name="ownerAddress"
            value={this.state.ownerAddress}
            type="text"
            disabled />
        </label>
        <br />
        <label>
          Owner Name:
          <input
            name="ownerName"
            value={this.state.ownerName}
            type="text"
            onChange={this.handleInputChange} />
        </label>
        <br />
        <label>
          Owner Email:
          <input
            name="ownerEmail"
            value={this.state.ownerEmail}
            type="text"
            onChange={this.handleInputChange} />
        </label>
        <br />
        <label>
          Syllabus URL:
          <input
            name="syllabusURL"
            value={this.state.syllabusURL}
            type="text"
            onChange={this.handleInputChange} />
        </label>
        <br />
        {/*
        <label>
          Number of members:
          <input
            name="numberOfMembers"
            type="number"
            value={this.state.numberOfMembers}
            onChange={this.handleInputChange} />
        </label>
        */}
        <input type="submit" value="Submit" />
      </form>
    );
  }
}

export default AddStudy;
