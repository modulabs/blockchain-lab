import React from "react";
import { BrowserRouter as Router, Route, Link } from "react-router-dom";
import StudyManagement from './components/StudyManagement'
import StudyDescription from './components/StudyDescription'

function BasicExample() {
  return (
    <Router>
      <div>
        <Route exact path="/" component={Home} />
        <Route path={`/studies/:studyId`} component={StudyDescription} />
        <Route path="/about" component={About} />
        <Route path="/studies" component={Studies} />
        <Route path="/my_studies" component={MyStudies} />
      </div>
    </Router>
  );
}

function Home() {
  return (
    <div>
    <div>
      <h1>Blockchain Lab</h1>
      <ul>
        <li>
          <Link to="/">Home</Link>
        </li>
        <li>
          <Link to="/about">About</Link>
        </li>
        <li>
          <Link to="/studies">Studies</Link>
        </li>
        <li>
          <Link to="/my_studies">My Studies</Link>
        </li>
      </ul>

      <hr />

    </div>
    </div>
  );
}

function About() {
  return (
    <div>
      <h2>About</h2>
    </div>
  );
}

function Studies({ match }) {
  return (
    <div>
      <h2>Studies</h2>
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

function MyStudies({ match }) {
  return (
    <div>
      <h2>My Studies</h2>
      <ul>
        <li>
          <Link to={`${match.url}/my/wed_blockchain`}>wed_blockchain</Link>
        </li>
      </ul>

      <Route path={`${match.path}/my/:studyId`} component={StudyManagement} />
      <Route
        exact
        path={match.path}
        render={() => <h3>Please select a topic.</h3>}
      />
    </div>
  );
}

function Study({ match }) {
  return (
    <div>
      <h3>{match.params.studyId}</h3>
    </div>
  );
}

export default BasicExample;
