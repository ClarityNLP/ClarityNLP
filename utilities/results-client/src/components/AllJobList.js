import React, { Component } from 'react';
import axios from 'axios';
import { Table } from 'reactstrap';

class AllJobList extends Component {


    constructor(props) {
        super(props);
        this.base_url = props.url;

        this.state = {
            jobs: []
        };
    }



    componentDidMount() {
        let url = this.base_url + 'phenotype_jobs/ALL';
        axios.get(url).then(response => {
            this.setState(prevState => ({
                jobs: response.data
            }));
        });
    }



    render() {
        const header_items =  ["Job ID", "Name", "Status", "Phenotype ID", "Owner", "Date", "Download" ].map((h) => {
            return <th key={h}>{h}</th>;
        });
        const job_items = this.state.jobs.map((p) => {
            return <tr className="JobStatusRow" key={p.nlp_job_id} >
                <td>{p.nlp_job_id}</td>
                <td>{p.phenotype_name}</td>
                <td>{p.status}</td>
                <td>{p.phenotype_id}</td>
                <td>{p.owner}</td>
                <td>{p.date_started}</td>
                <td>
                    <a href={ this.props.url + "job_results/" + p.nlp_job_id + "/phenotype_intermediate"}>Features</a>
                    <span> | </span>
                    <a href={ this.props.url + "job_results/" + p.nlp_job_id + "/phenotype"}>Cohort</a>
                </td>
            </tr>;
        });

        return (
            <div className="JobList">
                <div className="SubHeader">
                    NLQPL Jobs
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
            </div>
        );
    }
}

export default AllJobList;