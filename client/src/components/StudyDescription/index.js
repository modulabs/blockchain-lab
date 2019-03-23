import React, { Component } from "react";

import "./index.scss";

class StudyDescription extends Component {

  render() {
    return (
      <div className="StudyDescription">

        <div className="header">
          <div className="background">
            <div className="left">
              <h1>Wednesday Blockchain</h1>
            </div>
          </div>
        </div>
        <div class="row">
          <div class="col" >
            <a href="#introduction">
              Introduction
            </a>
          </div>
          <div class="col">
            <a href="#syllabus">
              Syllabus
            </a>
          </div>
          <div class="col">
            <a href="#reviews">
              Reviews
            </a>
          </div>
          <div class="col">
            <a href="#instructors">
              Instructors
            </a>
          </div>
          <div class="col">
            <a href="#enrollment">
              Enrollment
            </a>
          </div>
          <div class="col">
            <a href="#faq">
              FAQ
            </a>
          </div>
        </div>
        <br />
        <div className="container">
        <div id="introduction" className="introduction">
          <h3 className="about">About this course</h3>
          <p>We study Mastering Ethereum every Wednesday.</p>
          This course will introduce you to the basic elements of academic information seeking - we will explore the search process from defining a strategy to evaluating and documenting your search results.

Attending the course will make you a proficient information seeker. You will learn how to carry out comprehensive literature searches based on your own research assignment. You will be guided through the various information seeking steps from selecting relevant search strategies and techniques to evaluating your search results, documenting your search process and citing your sources.

Attending the course will enable you to:
•	Identify your information need
•	Evaluate databases and other information resources
•	Set up search strategies and use various search techniques
•	Formulate search strings based on your own research assignment
•	Identify relevant material types
•	Undertake critical evaluation of your sources
•	Search more efficiently on the internet
•	Avoid plagiarism
•	Cite correctly
•	Work with reference management
•	Document your search process

The course is intended for undergraduate students but the lessons will be useful to anyone who is interested in becoming better at finding scientific information. There are no formal requirements for the course.

The series consists of 21 lectures that are organized into three modules. The lectures include small assignments and quizzes (to check comprehension).
The lectures will each touch upon a topic that is essential to the information seeking process. To get the most out of the lecture series, we recommend that you access the lectures while you are working on an academic paper. We also recommend that you watch the lectures in the order in which we have structured them.
We recommend that you create and fill out a log book while attending the lectures. We have created a log book template that you can use during the course.

The lecture series has been developed in collaboration between information specialists at University of Copenhagen and Technical University of Denmark
        </div>
        <div id="syllabus">Syllabus
        Preparing your search process
In Module 1, we focus on preparation. We explain how to use a log book to document your searches, provide ideas for generating search terms,
introduce you to various types of literature, material and information resources, and to reference management.
Performing your searches
In module 2, you will learn to search for and find information. You will learn how to set up a search strategy and you will be introduced to
various search methods and search techniques.
Evaluating your search results
In module 3, you will learn how to evaluate, use and document your search results. You will get tips on how to critically assess information, you
will be introduced to concepts like copyright and plagiarism, and you will learn how to insert citations and bibliographies into your papers.
        </div>
        <div id="reviews">Reviews
        최상위 리뷰
        대학: GZ•SEP 11TH 2017
        A detailed review of one of the most important skills in academic research: information seeking. In particular, I enjoyed the tutorials on Mendeley and reference management tools. Highly recommended!

        대학: PD•FEB 14TH 2018
        Great Course for people who are new to research. This course provides an overview of the various components of the journey called research.\n\nThank you!
        </div>
        <div id="instructors">Instructors</div>
        <div id="enrollment">Enrollment</div>
        <div id="faq">FAQ
        강의 및 과제를 언제 이용할 수 있게 되나요?

        강좌에 등록하면 바로 모든 비디오, 테스트 및 프로그래밍 과제(해당하는 경우)에 접근할 수 있습니다. 상호 첨삭 과제는 이 세션이 시작된 경우에만 제출하고 검토할 수 있습니다. 강좌를 구매하지 않고 살펴보기만 하면 특정 과제에 접근하지 못할 수 있습니다.

        이 수료증을 구매하면 무엇을 이용할 수 있나요?

        수료증을 구매하면 성적 평가 과제를 포함한 모든 강좌 자료에 접근할 수 있습니다. 강좌를 완료하면 전자 수료증이 성취도 페이지에 추가되며, 해당 페이지에서 수료증을 인쇄하거나 LinkedIn 프로필에 수료증을 추가할 수 있습니다. 강좌 콘텐츠만 읽고 살펴보려면 해당 강좌를 무료로 청강할 수 있습니다.

        환불 규정은 어떻게 되나요?

        결제일 기준 2주 후 또는 (방금 시작된 강좌의 경우) 강좌의 첫 번째 세션이 시작된 후 2주 후 중에서 나중에 도래하는 날짜까지 전액 환불받을 수 있습니다. 2주 환불 기간 이내에 강좌를 완료했더라도 강좌 수료증을 받았으면 환불받을 수 없습니다. 전체 환불 정책을 확인하세요.

        재정 지원을 받을 수 있나요?

        예, Coursera는 수업료를 지급하기 어려운 학습자들에게 재정 지원을 제공합니다. 왼쪽의 "등록" 버튼 아래에 있는 재정 지원 링크를 클릭하면 재정 지원을 신청할 수 있습니다. 이 링크를 클릭하면 신청서를 작성하라는 메시지가 나타나며, 신청서가 승인되면 통지를 받게 됩니다. 자세히 알아보세요.
        </div>
        </div>
      </div>
    );
  }
}

export default StudyDescription;
