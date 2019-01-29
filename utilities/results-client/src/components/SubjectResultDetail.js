import React, {Component} from 'react';
import {Button} from 'reactstrap';
import {FaArrowLeft, FaArrowRight} from 'react-icons/fa';
import PhenotypeDetail from "./PhenotypeDetail";
import axios from 'axios';


const button_colors = ['primary', 'info', 'success', 'secondary', 'warning', 'danger'];
const placeholder = <div/>;

class SubjectResultDetail extends Component {

    constructor(props) {
        super(props);
        this.showPhenotype = this.showPhenotype.bind(this);
        this.isActivePhenotype = this.isActivePhenotype.bind(this);
        this.getChildButtons = this.getChildButtons.bind(this);
        this.showPhenotypeTypDetail = this.showPhenotypeTypDetail.bind(this);
        this.state = {
            subject: props.subject,
            results: props.results,
            orig_results: props.results,
            loading: false,
            config: props.config,
            idx: props.idx,
            total: props.total,
            selected_result: {},
            selected_result_index: -1,
            phenotype_id: props.phenotype_id,
            job: props.job,
            job_id: props.job.nlp_job_id,
            finals: [],
            ops: {},
            entities: {}
        };
    }


    componentDidMount() {
        let get_url = this.props.url + 'phenotype_structure/' + this.state.phenotype_id;
        axios.get(get_url).then(response => {
            this.setState({
                finals: response.data['finals'],
                ops: response.data['operations'],
                entities: response.data['data_entities']
            })
        });
    }

    componentDidUpdate(prevProps) {
        // console.log(this.props)
        if (prevProps.idx !== this.props.idx) {
            this.setState({
                subject: this.props.subject,
                results: this.props.results,
                config: this.props.config,
                idx: this.props.idx,
                total: this.props.total,
                phenotype_id: this.props.phenotype_id
            });
            if (this.props.results.length > 0) {
                this.setState({
                    selected_result: this.props.results[0],
                    selected_result_index: 0
                });
            }
        }

    }

    showPhenotype(data, index, e) {
        console.log(data);
        this.setState({
            selected_result: data,
            selected_result_index: index,
            results: this.state.orig_results
        });
    }

    showPhenotypeTypDetail(name) {
        if (this.state.loading) {
            console.log("wait a minute for loading");
            return;
        }
        this.setState({
            "loading": true,
            "results": []
        }, () => {
            let get_url = this.props.url + 'phenotype_feature_results/' + this.state.job_id + '/' + name
                + "/" + this.state.subject.subject;
            axios.get(get_url).then(response => {
                this.setState({
                    results: response.data,
                    loading: false
                })
            });
        });
    }

    isActivePhenotype(index) {
        let className = "PhenotypeDetailButtons ";
        if (index === this.state.selected_result_index) {
            className += " active";
        }
        return className;
    }

    getChildButtons(step, index, current_level, current_label) {

        if (!('data_entities' in step)) {
            return placeholder;
        }
        let new_level = current_level + 1;

        return step['data_entities'].map((d, d_index) => {
            let new_label = (current_label + "." + d_index);
            let obj = {};
            if (d in this.state.entities) {
                obj = this.state.entities[d];
            } else {
                obj = this.state.ops[d];
            }
            let child_entities = placeholder;
            if (obj) {
                if ('data_entities' in obj) {
                    child_entities = this.getChildButtons(obj, d_index, new_level, new_label);
                }
                let name = obj ? obj['name'] : d;
                return (<div key={name}>
                    <Button color={button_colors[new_level]} className="PhenotypeDetailButtons"
                            onClick={(e) => this.showPhenotypeTypDetail(name)}
                    >
                   <span className="PhenotypeSubDetailButtons">
                       { new_label + " " + name}</span>

                    </Button>
                    {child_entities}
                </div>);
            } else {
                return <div key={d}/>;
            }
        });
    }

    render() {
        let {subject, results, config,  total, finals} = this.state;

        let results_nav_view = <div />;
        if (finals) {
            results_nav_view = finals.map((d, index) => {
                let current_label = (index + 1);
                return (<div key={index}>
                    <Button onClick={(e) => this.showPhenotype(d, index, e)}
                            className="PhenotypeDetailButtons" color={button_colors[0]}>
                        { current_label + " " + d['name'] }</Button>
                    {this.getChildButtons(d, index, 0, current_label)}
                </div>);
            });

        }
        let results_type = typeof results;
        if (results_type === 'string') {
            results = JSON.parse(results);
        }
        let phenotype_results_detail = results.map((r, index) => {
            return (<PhenotypeDetail url={this.props.url} key={r._id} selected_result={r} selected_result_index={index}
                             config={config} subject={subject._id} job_id={this.state.job_id} showPhenotypeTypDetail={this.showPhenotypeTypDetail}/> );
        });
        let detail_count = results.length;

        return (
            <div className="container-fluid">
                <div className="row SubjectNavRow">

                    <small className="SubjectDetailNavigation">
                        <Button outline onClick={(e) => this.props.navigateSubject(-1, e)}><FaArrowLeft/></Button>
                        <span className="SubjectNavigationPosition"> {subject.index + 1}</span>
                        <span className="SubjectNavigationPosition"> of </span>
                        <span className="SubjectNavigationPosition"> {total} </span>
                        <Button outline onClick={(e) => this.props.navigateSubject(1, e)}><FaArrowRight/></Button>
                    </small>
                    <h5 className="SubjectDetailHeader float-lg-right">{subject._id + " (" + detail_count + " records)"}</h5>
                </div>
                <div className="row SubjectDetailBody">
                    <div className="col-2">
                        {results_nav_view}
                    </div>
                    <div className="col-8">
                        <div>
                            {phenotype_results_detail}
                        </div>
                    </div>
                    <div className="col-2">

                    </div>
                </div>
            </div>
        )
    }
}

export default SubjectResultDetail;
