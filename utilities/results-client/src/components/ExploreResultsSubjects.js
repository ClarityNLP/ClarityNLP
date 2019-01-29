import React, { Component } from 'react';
import { Table } from 'reactstrap';
import axios from "axios";
import SubjectResultDetail from './SubjectResultDetail';

class ExploreResultsSubjects extends Component {

    constructor(props) {
        super(props);
        this.selectSubject = this.selectSubject.bind(this);
        this.navigateSubject = this.navigateSubject.bind(this);
        this.state = {
            show_subject_list: true,
            subjects: [],
            selected_subject: {},
            selected_index: 0,
            current_results: [],
            config: {}
        };
    }

    selectSubject(subject, event) {
        let phenotype_final = true;
        let job_id = this.props.job.nlp_job_id;
        let url = this.props.url + 'phenotype_subject_results/' + job_id + '/' + phenotype_final + '/' + subject._id;
        axios.get(url).then(response => {
            //console.log(response.data);
            this.setState(prevState => ({
                selected_subject: subject,
                selected_index: subject['index'],
                current_results: response.data,
                show_subject_list: false
            }));
        });
    }

    navigateSubject(direction, event) {
        let new_index = this.state.selected_index + direction;
        let subjects_length = this.state.subjects.length;
        let back_to_list = false;
        if (new_index < 0) {
            // new_index = subjects_length - 1;
            back_to_list = true;
        }
        if (new_index > (subjects_length - 1)) {
            //new_index = 0
            back_to_list = true;
        }
        if (!back_to_list) {
            let new_subject = this.state.subjects[new_index];
            this.selectSubject(new_subject, {})
        } else {
            this.setState(prevState => ({
                selected_subject: {},
                selected_index: 0,
                show_subject_list: true
            }));
        }
    }

    componentDidMount() {

        let phenotype_final = true;
        let job_id = this.props.job.nlp_job_id;

        let url = this.props.url + 'phenotype_subjects/' + job_id + '/' + phenotype_final;
        axios.get(url).then(response => {
            let s_list = response.data;
            for (let i = 0; i < s_list.length; i++) {
                s_list[i]['index'] = i;
                s_list[i]['subject'] = s_list[i]['_id']
            }
            s_list = s_list.filter(s => s['subject'] !== '');

            this.setState(prevState => ({
                subjects: s_list
            }));
            this.props.setSubjects(s_list);
        });
        this.setState(prevState => ({
            config: JSON.parse(this.props.job.config)
        }));
    }

    render() {
        let phenotype_id = this.props.job.phenotype_id;
        const header_items =  ["Subject", "Matching Events" ].map((h) => {
            return <th key={h}>{h}</th>;
        });
        const subjects = this.state.subjects.map((p) => {
            return <tr className="SubjectRow" key={p._id} onClick={(e) => this.selectSubject(p, e)}>
                <td>{p._id}</td>
                <td>{p.count}</td>
            </tr>;
        });
        return (
          <div>
            {this.state.subjects.length > 0 ?
                <div>
                    {this.state.show_subject_list ?
                        <Table className="SubjectTable" striped>
                            <thead>
                            <tr>
                                {header_items}
                            </tr>
                            </thead>
                            <tbody>
                            {subjects}
                            </tbody>
                        </Table>
                        :
                        <div>
                            <SubjectResultDetail url={this.props.url} phenotype_id={phenotype_id} job={this.props.job}
                                                config={this.state.config} subject={this.state.selected_subject}
                                                 results={this.state.current_results} idx={this.state.selected_index}
                                                total={this.state.subjects.length} navigateSubject={this.navigateSubject}/>
                        </div>
                    }
                </div> :
                <div className="emptyResults">
                  No results present.
                </div>
            }
          </div>
        )
    }
}

export default ExploreResultsSubjects;
