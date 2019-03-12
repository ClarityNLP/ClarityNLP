import React, { Component } from "react";
import Card from "../Card";

export default class Results extends Component {
    constructor(props) {
        super(props);

        this.state = {
            job_data: []
        };
    }

    componentDidUpdate(prevProps) {
        if (prevProps.app.jobs !== this.props.app.jobs) {
            this.setContent();
        }
    }

    setContent = () => {
        const { jobs } = this.props.app;
        let data = [];

        data = jobs.map((job, i) => {
            return (
                <tr
                    key={"job" + i}
                    className="job_row"
                    onClick={() => {
                        this.redirectToJob(job.nlp_job_id);
                    }}
                >
                    <td>{job.name}</td>
                    <td>{job.status}</td>
                </tr>
            );
        });

        this.setState({
            job_data: data
        });
    };

    redirectToJob = job_id => {
        window.location =
            process.env.REACT_APP_RESULT_VIEWER_URL + "?job=" + job_id;
    };

    render() {
        const { job_data } = this.state;

        return (
            <Card
                className="results"
                heading="Results"
                cta_label="See All Results"
                cta_href={process.env.REACT_APP_RESULT_VIEWER_URL}
            >
                <div className="results_container">
                    <table className="table is-hoverable is-striped is-fullwidth">
                        <thead>
                            <tr>
                                <th>Job Name</th>
                                <th>Job Status</th>
                            </tr>
                        </thead>
                        <tbody>{job_data}</tbody>
                    </table>
                </div>
            </Card>
        );
    }
}
