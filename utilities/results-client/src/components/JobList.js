import React, { Component } from 'react';
import axios from 'axios';
import ResultViewer from './ResultViewer';
import TableJobs from './TableJobs';

class JobList extends Component {


    constructor(props) {
        super(props);
        this.base_url = props.url;
        this.luigi = props.luigi;
        this.selectJob = this.selectJob.bind(this);
        this.resetJobsList = this.resetJobsList.bind(this);
        this.getAllJobs = this.getAllJobs.bind(this);
        this.getFilter = this.getFilter.bind(this);

        this.state = {
            jobs: [],
            filtered_jobs: [],
            job: {},
            show_list: true,
            job_param: props.job,
            filter: ''
        };
    }

    getFilter(filter) {
        setTimeout(() => {
            let new_jobs = this.state.jobs.filter((f) => {
                let name = f.phenotype_name.toLowerCase();
                let status = f.status.toLowerCase();
                let nlpql = f.nlpql.toLowerCase();
                let desc = f.description.toLowerCase();

                let search = name + " " + status + " " + nlpql + " " + desc;
                return search.indexOf(filter.toLowerCase()) >= 0;
            });

            this.setState({
                filter: filter,
                filtered_jobs: new_jobs
            });
        }, 25);
    }

    getAllJobs() {
        this.setState(prevState => ({
            jobs: [],
            show_list: true
        }));
        let url = this.base_url + 'phenotype_jobs/ALL';

        axios.get(url).then(response => {
            let filtered_jobs = response.data.filter((f) => {
                let name = f.phenotype_name.toLowerCase();
                return name.indexOf(this.state.filter) >= 0;
            });
            this.setState(prevState => ({
                jobs: response.data,
                filtered_jobs: filtered_jobs
            }));
        });
    }

    componentDidMount() {
        this.getAllJobs();
        if (this.state.job_param !== null) {
            let url = this.base_url + 'phenotype_job_by_id/' + this.state.job_param;
            console.log(this.state.job_param);
            axios.get(url).then(response => {
                this.setState(prevState => ({
                    job: response.data,
                    show_list: false
                }));
            });
        }
    }

    resetJobsList() {
        this.setState(prevState => ({
            job: {},
            show_list: true
        }));
    }

    selectJob(p, e) {
        //console.log(p);
        if (p !== null && p['nlp_job_id'] !== -1) {
            this.setState(prevState => ({
                job: p,
                show_list: false
            }));
        }

    }

    render() {
        return (
            <div className="JobList">
                {this.state.show_list ?
                    <TableJobs jobs={this.state.filtered_jobs} selectJob={this.selectJob} url={this.props.url}
                               luigi={this.luigi} refreshJobs={this.getAllJobs} getFilter={this.getFilter} filter={this.state.filter}/> :
                    <ResultViewer resetJobsList={this.resetJobsList} job={this.state.job} url={this.props.url}/>}
            </div>
        );
    }
}

export default JobList;