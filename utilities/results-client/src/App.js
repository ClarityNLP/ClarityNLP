import React, { Component } from 'react';
import logo from './gtri.png';
import './App.css';
import JobList from "./components/JobList";
import JobRunner from "./components/JobRunner";
import { Collapse, Navbar, NavbarToggler, NavbarBrand, Nav, NavItem, NavLink } from 'reactstrap';
import {
    UncontrolledDropdown,
    DropdownToggle,
    DropdownMenu,
    DropdownItem } from 'reactstrap';
import { FaCog } from 'react-icons/fa';

// https://html-online.com/articles/get-url-parameters-javascript/
function getUrlVars() {
    let vars = {};
    window.location.href.replace(/[?&]+([^=&]+)=([^&]*)/gi, function(m,key,value) {
        vars[key] = value;
    });
    return vars;
}

class App extends Component {
    constructor(props) {
        super(props);
        this.toggle = this.toggle.bind(this);
        this.setMode = this.setMode.bind(this);
        this.params = getUrlVars();
        let job_id = null;
        if ('job' in this.params) {
            job_id = this.params['job']
        }
        if ('job_id' in this.params) {
            job_id = this.params['job_id']
        }
        this.state = {
            isOpen: false,
            mode: 'results',
            job: job_id
        };
    }

    toggle() {
        this.setState({
            isOpen: !this.state.isOpen
        });
    }

    setMode(mode) {
        this.setState({
            'mode': mode,
            'collapsed': true
        })
    }


  render() {
    let main = <div />;
    console.log(process.env);
    if (this.state.mode === 'results') {
        main = <JobList url={process.env.REACT_APP_CLARITY_NLP_URL} luigi={process.env.REACT_APP_LUIGI_URL} job={this.state.job}/>;
    } else if (this.state.mode === 'runner') {
        main = <JobRunner url={process.env.REACT_APP_CLARITY_NLP_URL}/>;
    }
    return (
      <div className="App">
          <Navbar expand="md" className="App-header" dark>
              <NavbarBrand href="/" className="mr-auto"><img src={logo} className="App-logo" alt="logo" /> <div className="App-name">ClarityNLP</div></NavbarBrand>
              <NavbarToggler onClick={this.toggle} />
              <Collapse isOpen={this.state.isOpen} navbar>
                  <Nav className="ml-auto" navbar>
                      <NavItem>
                          <NavLink className="NavLink"  onClick={() => this.setMode('runner')}>NLPQL Runner</NavLink>
                      </NavItem>
                      <NavItem>
                          <NavLink className="NavLink" onClick={() => this.setMode('results')}>Results Viewer</NavLink>
                      </NavItem>
                      <UncontrolledDropdown nav inNavbar>
                          <DropdownToggle nav caret>
                              <FaCog/>
                          </DropdownToggle>
                          <DropdownMenu right>
                              <DropdownItem href="https://claritynlp.readthedocs.io/en/latest/" target="_blank">
                                  Documentation
                              </DropdownItem>
                              <DropdownItem href="https://github.com/ClarityNLP/ClarityNLP" target="_blank">
                                  GitHub
                              </DropdownItem>

                          </DropdownMenu>
                      </UncontrolledDropdown>
                  </Nav>
              </Collapse>
          </Navbar>

        <div className="App-intro container-fluid">
            {main}
        </div>
      </div>
    );
  }
}

export default App;
