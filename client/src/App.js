import React from "react";
import { BrowserRouter as Router, Route, Link } from "react-router-dom";

import StudyManagement from './components/StudyManagement'
import StudyDescription from './components/StudyDescription'
import AddStudy from './components/AddStudy'

import './App.css'

function BasicExample() {
  return (
    <Router>
      <div>
        <a href="/"><img src="blockchainlab-logo.svg"
             class="blockchainlab_logo" /></a>
        <Route exact path="/" component={Home} />
        <Route path={`/add_study`} component={AddStudy} />
        <Route path={`/studies/:studyId`} component={StudyDescription} />
        <Route path={`/my_studies/:studyId`} component={StudyManagement} />
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
      <Link to='/add_study' className="button">Add Study</Link>
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

export default BasicExample;
