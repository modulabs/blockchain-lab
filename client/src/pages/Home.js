import React from "react";
import { Link } from "react-router-dom";

const Home = () => {
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

export default Home;
