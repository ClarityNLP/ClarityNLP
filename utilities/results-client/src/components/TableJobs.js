import React, { Component } from 'react';
import { Table, Input, Modal, ModalHeader, ModalBody, ModalFooter, Button } from 'reactstrap';
import Moment from 'react-moment';
import 'moment-timezone';
import { FaCode, FaFileAlt, FaStop, FaTrash } from 'react-icons/fa';
import ReactJson from 'react-json-view'
import axios from "axios";


class TableJobs extends Component {

    constructor(props) {
        super(props);
        this.getStatus = this.getStatus.bind(this);
        this.keyUpHandler = this.keyUpHandler.bind(this);
        this.toggle = this.toggle.bind(this);
        this.showJSON = this.showJSON.bind(this);
        this.showNLPQL = this.showNLPQL.bind(this);
        this.killJob = this.killJob.bind(this);
        this.jobToggle = this.jobToggle.bind(this);
        this.deleteJob = this.deleteJob.bind(this);
        this.takeSeriousAction = this.takeSeriousAction.bind(this);
        if (props.filter !== '') {
            props.getFilter(props.filter);
        }
        this.state = {
            jobs: props.jobs,
            modal: false,
            modal_title: "View NLPQL",
            modal_type: "NLPQL",
            nlpql: '',
            config: {},
            job_modal: false,
            job_modal_title: "Kill Job",
            job_modal_type: "KILL",
            job_id:'-1',
            job_danger_status: '',
            can_continue_action: true,
            filter: props.filter
        };
    }

    toggle() {
        this.setState({
            modal: !this.state.modal
        });
    }

    jobToggle() {
        this.setState({
            job_modal: !this.state.job_modal
        });
    }

    showJSON(job, event) {

        this.setState({
            modal: true,
            config: JSON.parse(job.config),
            modal_title: "JSON (" + job.phenotype_name + ")",
            modal_type: "JSON",
            nlpql: ''
        });
    }

    showNLPQL(job, event) {
        this.setState({
            modal: true,
            config: {},
            modal_title: "NLPQL (" + job.phenotype_name + ")",
            modal_type: "NLPQL",
            nlpql: job.nlpql
        });
    }

    killJob(jobId) {
        this.setState({
            job_modal: true,
            job_modal_title: "Kill job " + jobId,
            job_modal_type: "KILL",
            job_id: jobId,
            job_danger_status: ''
        });
    }

    deleteJob(jobId) {
        this.setState({
            job_modal: true,
            job_modal_title: "Delete job " + jobId,
            job_modal_type: "DELETE",
            job_id: jobId,
            job_danger_status: ''
        });
    }

    takeSeriousAction() {
        this.setState({
            can_continue_action: false
        });
        let action_url = this.props.url + "delete_job/" + this.state.job_id;
        if (this.state.job_modal_type === "KILL") {
            action_url = this.props.url + "kill_job/" + this.state.job_id
        }

        axios.get(action_url).then(response => {
            this.setState({
                job_danger_status: response.data,
                job_id: -1
            });
            this.props.refreshJobs();
            setTimeout(()=> {
                this.setState({
                    job_modal: false,
                    can_continue_action: true
                });
            }, 100)
        });
    }

    getStatus(row) {
        if (row.status !== "IN_PROGRESS") {
            return (
                <span>{row.status}</span>
            );
        } else {
            let luigi = this.props.luigi + '/static/visualiser/index.html#search__search=job=' + row.nlp_job_id;
            return <span><a target="_blank" href={luigi}>{row.status}</a></span>
        }
    }

    keyUpHandler() {
        let txt = document.getElementById('jobs_filter').value.toLowerCase();
        this.props.getFilter(txt);

    };

    componentDidUpdate(prevProps) {
        if (this.props.jobs.length !== prevProps.jobs.length) {
            this.setState({
                jobs: this.props.jobs
            })
        }

        if (this.props.filter !== this.state.filter) {
            this.setState({
                filter: this.props.filter
            });
            // this.props.getFilter(this.props.filter);
        }
    }

    componentDidMount() {
        if (this.state.filter !== '') {
            document.getElementById('jobs_filter').value = this.state.filter;
        }
    }

    render() {
        const header_items =  ["Job ID", "Name", "Phenotype ID", "Status", "Date", "Download CSV", "Actions"].map((h) => {
            return <th key={h}>{h}</th>;
        });
        let job_items = this.state.jobs.map((p) => {
            return <tr className="JobRow" key={p.nlp_job_id} >
                <td onClick={(e) => this.props.selectJob(p, e)}>{p.nlp_job_id}</td>
                <td onClick={(e) => this.props.selectJob(p, e)} className="PhenotypeName"><span>{p.phenotype_name}</span></td>
                <td onClick={(e) => this.props.selectJob(p, e)}>{p.phenotype_id}</td>
                <td onClick={(e) => this.props.selectJob(p, e)}>{this.getStatus(p)}</td>
                <td style={{"minWidth": "120px"}} onClick={(e) => this.props.selectJob(p, e)}><Moment format="MMM D, YYYY h:mm a">
                    {p.date_started}
                </Moment></td>
                <td style={{"minWidth": "240px"}}>
                    <a href={ this.props.url + "job_results/" + p.nlp_job_id + "/features"}>Features</a>
                    <span> | </span>
                    <a href={ this.props.url + "job_results/" + p.nlp_job_id + "/cohort"}>Cohort</a>
                    <span> | </span>
                    <a href={ this.props.url + "job_results/" + p.nlp_job_id + "/annotations"}>Annotations</a>
                </td>
                <td style={{"minWidth": "100px"}}>
                    <span title="View NLPQL" className="JobListIcons" onClick={(e) => this.showNLPQL(p, e)}><FaFileAlt /></span>
                    <span title="View JSON" onClick={(e) => this.showJSON(p, e)}><FaCode/></span>
                    <span style={{"paddingRight": "20px"}}>&nbsp;</span>
                    {p.status === "IN_PROGRESS" ?
                        <span title="Kill Job" onClick={(e) => this.killJob(p.nlp_job_id)}><FaStop/></span>
                        :
                        <span title="Delete Job" onClick={(e) => this.deleteJob(p.nlp_job_id)}><FaTrash/></span>
                    }
                </td>
            </tr>;
        });

        return (
            <div>
                <div className="SubHeader">
                    NLPQL Results
                    <div className="float-lg-right">
                        <Input type="text" name="filter" id="jobs_filter" placeholder="Search..." onKeyUp={this.keyUpHandler} />
                    </div>
                </div>
                <Table striped>
                    <thead>
                        <tr>
                         {header_items}
                        </tr>
                    </thead>
                    <tbody>
                        {job_items}
                    </tbody>
                </Table>
                <Modal isOpen={this.state.modal} toggle={this.toggle} className="ReportModal">
                    <ModalHeader toggle={this.toggle}>{this.state.modal_title}</ModalHeader>
                    <ModalBody>
                        {this.state.modal_type === "NLPQL" ?
                            <div className="ReportTextPreview">{this.state.nlpql}</div> :
                            <ReactJson src={this.state.config} displayObjectSize={false} displayDataTypes={false}/>
                        }
                    </ModalBody>
                    <ModalFooter>
                        <Button color="secondary" onClick={this.toggle}>Close</Button>
                    </ModalFooter>
                </Modal>
                <Modal isOpen={this.state.job_modal} toggle={this.jobToggle} className="JobModal">
                    <ModalHeader toggle={this.jobToggle}>{this.state.job_modal_title}</ModalHeader>
                    <ModalBody>
                        { "Are you sure you want to " + this.state.job_modal_type.toLowerCase() + " this job?"}
                    </ModalBody>
                    <ModalFooter>
                        <Button color="danger" onClick={this.takeSeriousAction}>Continue</Button>
                        <Button color="secondary" onClick={this.jobToggle}>Cancel</Button>
                    </ModalFooter>
                </Modal>
            </div>

        )
    }
}

export default TableJobs;