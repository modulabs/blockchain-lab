import React from "react";
import { Route, Link } from "react-router-dom";

const MyStudies = ({ match }) => {
  return (
    <div>
      <h2>My Studies</h2>
      <ul>
        <li>
          <Link to={`${match.url}/wed_blockchain`}>wed_blockchain</Link>
        </li>
      </ul>

      <Route
        exact
        path={match.path}
        render={() => <h3>Please select a topic.</h3>}
      />
    </div>
  );
}

export default MyStudies;