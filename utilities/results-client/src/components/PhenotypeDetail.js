import React, { Component } from 'react';
import axios from 'axios';
import EntityFrame from './EntityFrame';
import { FaCheck, FaTimes, FaStickyNote } from 'react-icons/fa';
import { Button, Modal, ModalHeader, ModalBody, ModalFooter, Input, Alert } from 'reactstrap';

const suffixes = ['_x', '_y'];

class PhenotypeDetail extends Component {

    constructor(props) {
        super(props);
        this.resetViewAll = this.resetViewAll.bind(this);
        this.writeFeedback = this.writeFeedback.bind(this);
        this.saveComments = this.saveComments.bind(this);
        this.toggle = this.toggle.bind(this);
        this.toggleAlert = this.toggleAlert.bind(this);
        this.onDismiss = this.onDismiss.bind(this);
        this.state = {
            view_mode: "all",
            selected_result_index: props.selected_result_index,
            selected_result: props.selected_result,
            results: [],
            successAlert: false,
            failureAlert:false
        };
        this.url = props.url;
        this.detailed_results = {};
        this.user_comments = "";
        // this.successful_export = false;
        // this.failed_export = false;

        this.ids = [];
        if ('_id' in props.selected_result) this.ids.push(props.selected_result['_id']);
        if ('_id_x' in props.selected_result) this.ids.push(props.selected_result['_id_x']);
        if ('_id_y' in props.selected_result) this.ids.push(props.selected_result['_id_y']);
        if ('_id_z' in props.selected_result) this.ids.push(props.selected_result['_id_z']);
        this.id_string = this.ids.join();
    }

    // Function to save the comment entered by the user
    saveComments() {
      let comment = document.getElementById("feedbackComments").value;
      this.user_comments = comment;
      this.toggle();
    }

    onDismiss() {
      this.setState({
          successAlert: false,
          failureAlert: false
      });
    }

    // Function to toggle between success and failure alerts
    toggleAlert(response) {
      if (response === true) {
        this.setState({
            successAlert: true,
            failureAlert: false
        });
      } else {
        this.setState({
            successAlert: false,
            failureAlert: true
        });
      }
    }

    // Function to write nlpql feedback back to mongoDB
    writeFeedback(option) {
      let data = {};
      data['feature'] = this.state.selected_result['nlpql_feature'];
      data['job_id'] = this.props.job_id;
      data['subject'] = this.props.subject;
      data['comments'] = this.user_comments;
      data["result_id"] = this.state.selected_result['_id'];
      data["report_id"] = this.state.selected_result['report_id'];
      if (option === 1) {
        data['is_correct'] = 'true';
      } else if (option === 2) {
        data['is_correct'] = 'false';
      } else {
          data['is_correct'] = '';
      }

      let payload = JSON.stringify(data);
      let request_url = this.url + 'write_nlpql_feedback';

      axios.post(request_url, payload, {
        headers: {
          'Content-Type': 'application/json'
        }
      })
      .then(response => {
          console.log(response.data);
          this.toggleAlert(true);
      })
      .catch(error => {
          console.log(error);
          this.toggleAlert(false);
      });
    }


    resetViewAll(detail_results) {
        if (!detail_results) {
            detail_results = this.detailed_results;
        }
        let {selected_result} = this.state;
        let results = [];
        if ('sentence_x' in selected_result) {
            results = suffixes.map((s, index) => {
                let id = selected_result['_id' + s];
                let detail = {};
                if (id in detail_results['indexes']) {
                    let detail_idx = detail_results['indexes'][id];
                    detail = detail_results['results'][detail_idx];
                }
                return {
                    "index": index,
                    "feature": selected_result['nlpql_feature' + s],
                    "report_date": selected_result['report_date' + s],
                    "text": selected_result['sentence' + s],
                    "id": id,
                    "detail": detail,
                    "report_id": selected_result['report_id' + s]

                };
            });
        } else {
            let text = '';
            const tags = ['sentence', 'text', 'report_text', 'term', 'value'];
            for (let i in tags) {
                let tag = tags[i];
                if (selected_result.hasOwnProperty(tag)) {
                    text = selected_result[tag];
                    break;
                }
            }
            if (text.length === 0) {
                text = JSON.stringify(selected_result);
            }
            results.push({
                "index": 0,
                "feature": selected_result['nlpql_feature'],
                "report_date": selected_result['report_date'],
                "text": text,
                "id": selected_result['_id'],
                "detail": selected_result,
                "report_id": selected_result['report_id']
            })
        }

        this.setState({
            results: results
        });
    }

    componentDidMount() {
        let get_url = this.url + 'phenotype_results_by_id/' + this.id_string;
        axios.get(get_url).then(response => {
            this.detailed_results = response.data;
            this.resetViewAll(response.data);
        });

    }

    componentDidUpdate(prevProps) {
        if (this.props.selected_result_index !== this.state.selected_result_index) {
            this.setState({
                selected_result_index: this.props.selected_result_index,
                selected_result: this.props.selected_result
            }, this.resetViewAll);
        }
    }

    toggle() {
      this.setState({
        modal: !this.state.modal
      });
    }

    render() {
        let {selected_result, selected_result_index, results} = this.state;
        let results_view = results.map((d) => {
             return (
                <EntityFrame key={d['index']} data={d} url={this.url} showPhenotypeTypDetail={this.props.showPhenotypeTypDetail}
                    nlpql_feature={selected_result.nlpql_feature}
                />
            );
        });

        return (
            <div >
                {selected_result_index > -1 ?
                    <div className="PhenotypeDetailMain">
                        <div><span className="h4"> {selected_result.nlpql_feature} </span>
                            {selected_result.raw_definition_text && selected_result.raw_definition_text.length > 0 ?
                            <small>  ({selected_result.raw_definition_text})</small> :
                                <span />}
                            <span className="float-lg-right">
                                <Button outline size="sm" color="success" onClick={() => { this.writeFeedback(1) }}><FaCheck/></Button> { " " }
                                <Button outline size="sm" color="danger" onClick={() => { this.writeFeedback(2) }}><FaTimes/></Button> { " " }
                                <Button outline size="sm" color="info" onClick={() => { this.toggle() }}><FaStickyNote/></Button> { " " }
                            </span>
                        </div>
                        {results_view}
                        {this.state.successAlert === true ?
                          <Alert color="success" toggle={this.onDismiss}><font size="3">Thank you for submitting feedback.</font></Alert> : <span />
                        }
                        {this.state.failureAlert === true ?
                          <Alert color="danger" toggle={this.onDismiss}><font size = "3">Could not submit feedback. Contact Admin.</font></Alert> : <span />
                        }
                    </div> :
                    <span/>

                }

                <div id = "commentsModal">
                  <Modal isOpen={this.state.modal} toggle={this.toggle} className={this.props.className}>
                    <ModalHeader toggle={this.toggle}>Enter Comment</ModalHeader>
                    <ModalBody>
                      <Input type="textarea" name="comments" id="feedbackComments" defaultValue={this.user_comments}></Input>
                    </ModalBody>
                    <ModalFooter>
                      <Button color="primary" onClick={() => { this.saveComments() }}>Save Comment</Button>{' '}
                    </ModalFooter>
                  </Modal>
                </div>

            </div>
        )
    }
}

export default PhenotypeDetail;
