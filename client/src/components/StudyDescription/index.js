import React, { Component } from "react";

import "./index.css";

class StudyDescription extends Component {

  render() {
    return (
      <div className="StudyDescription">
        <h1>Wednesday Blockchain</h1>
        <div class="row">
          <div class="col" >
            <a href="#introduction">
              Introduction
            </a>
          </div>
          <div class="col">
            Syllabus
          </div>
          <div class="col">
            Reviews
          </div>
          <div class="col">
            Instructors
          </div>
          <div class="col">
            Enrollment
          </div>
          <div class="col">
            FAQ
          </div>
        </div>
        <br />

        <div id="#introduction">
          <h3>Introduction</h3>
          <p>We study Mastering Ethereum every Wednesday.</p>
        </div>
        <div id="#syllabus">Syllabus</div>
        <div id="#reviews">Reviews</div>
        <div id="#instructors">Instructors</div>
        <div id="#enrollment">Enrollment</div>
        <div id="#faq">FAQ</div>
      </div>
    );
  }
}

export default StudyDescription;
