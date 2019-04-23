import React, { Component } from "react";
import { Route, Link } from "react-router-dom";

import { getLabDetail } from "../utils/getLabInfo";

class MyStudies extends Component {
  constructor(props) {
    super(props);
    this.state = {
      accounts: [], 
      studyContracts: [], 
      labOwner: null, 
      labName: null
    }
  }

  componentDidMount = async () => {
    const labInfo = await getLabDetail();
    console.log(labInfo);
    this.setState(labInfo);
  }

  render = () => {
    const { match } = this.props;
    return (
      <div>
        {
          this.state.labName !== null ? <h2>My Studies in {this.state.labName}</h2> : <h2>My Studies</h2>
        }
        
        {
          this.state.studyContracts.length === 0 ? <h3>No study found</h3>
            : <ul> 
            {
              this.state.studyContracts.map((contract, i) => {
                return <li key={i} >
                  <Link to={`${match.url}/${contract.studyName}?address=${contract.studyAddress}`}> { contract.studyName } </Link>
                </li>
              })
            } 
          </ul>  
        }
  
        <Route
          exact
          path={match.path}
          render={() => <h3>Please select a topic.</h3>}
        />
      </div>
    );
  }
} 

export default MyStudies;