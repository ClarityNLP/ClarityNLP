import React, { Component } from 'react';
import { Button,  ButtonGroup } from 'reactstrap';
import { FaArrowLeft } from 'react-icons/fa';
import RawResultsView from './RawResultsView';
import ExploreResultsSubjects from './ExploreResultsSubjects';

const EXPLORE = 1;
const ANNOTATE = 2;
const INTERMEDIATE = 3;
const ALL = 4;

class ResultViewer extends Component {


    constructor(props) {
        super(props);
        this.state = {
            mode_selected: 1,
            patient_count: 0
        };
        this.setSubjects = this.setSubjects.bind(this);
    }

    componentDidMount() {
    }

    componentDidUpdate(prevProps) {
        // console.log(this.props)
    }

    onRadioBtnClick(mode_selected) {
        this.setState({ mode_selected });
    }

    setSubjects(s) {
        if (s) {
            this.setState({
                'patient_count': s.length
            });
        }
    }

    render() {
        return (
            <div className="container-fluid">
                <div className="row">
                    <div className="col">
                        <h3><small><Button className="btn btn-light ArrowButtons" onClick={this.props.resetJobsList}><FaArrowLeft/></Button>
                        </small><span className="PhenotypeTitle">{this.props.job.phenotype_name}</span>
                            {  this.state.mode_selected === ANNOTATE  ?

                                <span/> :<span
                            className="PatientCount">{"  (" + this.state.patient_count + " subjects)"}</span>}
                            <small className="float-sm-right ToggleButtons"><ButtonGroup>
                                <Button onClick={() => this.onRadioBtnClick(EXPLORE)} active={this.state.mode_selected === EXPLORE}>Explore</Button>
                                <Button onClick={() => this.onRadioBtnClick(INTERMEDIATE)} active={this.state.mode_selected === INTERMEDIATE}>Features</Button>
                                <Button onClick={() => this.onRadioBtnClick(ALL)} active={this.state.mode_selected === ALL}>Cohort</Button>
                            </ButtonGroup></small>
                            { this.state.mode_selected === EXPLORE || this.state.mode_selected === ANNOTATE ?
                                <div>
                                    <ExploreResultsSubjects job={this.props.job} url={this.props.url} setSubjects={this.setSubjects} />
                                </div>:
                                <div>
                                    <RawResultsView job={this.props.job} mode={this.state.mode_selected} url={this.props.url} />
                                </div>
                                
                            }
                        </h3>
                    </div>
                </div>

            </div>
        )
    }
}

export default ResultViewer;