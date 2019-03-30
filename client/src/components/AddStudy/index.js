import React, { Component } from "react";

import "./index.scss";

class AddStudy extends Component {
  constructor(props) {
    super(props);
    this.state = {
    };

    this.handleInputChange = this.handleInputChange.bind(this);
    this.handleSubmit = this.handleSubmit.bind(this);
  }

  handleInputChange(event) {
    const target = event.target;
    const value = target.type === 'checkbox' ? target.checked : target.value;
    const name = target.name;

    this.setState({
      [name]: value
    });
  }

  handleSubmit(event) {
    alert('numberOfMembers: ' + this.state.numberOfMembers);
    event.preventDefault();
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
            type="text" />
        </label>
        <br />
        <label>
          Owner Email:
          <input
            name="ownerEmail"
            value={this.state.ownerEmail}
            type="text" />
        </label>
        <br />
        <label>
          Syllabus URL:
          <input
            name="syllabusURL"
            value={this.state.syllabusURL}
            type="text" />
        </label>
        <br />
        <label>
          Number of members:
          <input
            name="numberOfMembers"
            type="number"
            value={this.state.numberOfMembers}
            onChange={this.handleInputChange} />
        </label>
        <input type="submit" value="Submit" />
      </form>
    );
  }
}

export default AddStudy;
