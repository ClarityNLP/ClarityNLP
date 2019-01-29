import React, {Component} from 'react';
import {Cell, Column, Table} from 'fixed-data-table-2';
import axios from 'axios';
import _ from 'lodash';
import { Button, Modal, ModalHeader, ModalBody, ModalFooter, Form, FormGroup, Label, Input, Alert } from 'reactstrap';

const ALL = 4;
const page_size = 100;
const row_height = 80;
const header_height = 50;


// Based on example from https://github.com/schrodinger/fixed-data-table-2/blob/master/examples/PaginationExample.js
class PendingCell extends React.PureComponent {
    render() {
        const {data, rowIndex, columnKey, dataVersion, ...props} = this.props;
        const rowObject = data.getObjectAt(rowIndex);
        return (
            <Cell {...props}>
                {rowObject ? rowObject[columnKey] : 'pending'}
            </Cell>
        );
    }
}

const PagedCell = ({data, ...props}) => {
    const dataVersion = data.getDataVersion();
    return (
        <PendingCell
            data={data}
            dataVersion={dataVersion}
            {...props}>
        </PendingCell>
    );
};

class ResultData {
    constructor(callback, job, get_url) {

        this._dataList = [];
        this._end = page_size;
        this._pending = false;
        this._dataVersion = 0;
        this._callback = callback;
        this.job = job;
        this.get_url = get_url;
        this.new_last_id = '';
        this.size = page_size;
        this.no_more = false;
        this.columns = [];

        this.getDataStore(job, get_url, true);

    }

    getDataStore(job, get_url, first, resolve) {

        if (first) {
            axios.get(get_url).then(response => {

                if (response.data.success) {
                    let results = response.data.results;
                    this.new_last_id = response.data.new_last_id;
                    this.size = response.data.count;
                    this.no_more = response.data.no_more;
                    this.columns = response.data.columns;
                    this._dataList = results;
                }
                this._callback(page_size);


            });
        } else {
            axios.get(get_url + '?last_id=' + this.new_last_id).then(response => {
                if (response.data.success) {
                    let results = response.data.results;
                    if (resolve !== null) {
                        resolve({
                                last_id: response.data.new_last_id,
                                no_more: response.data.no_more,
                                results: results
                            });
                    }
                }
            });
        }

    }

    appendResults(results) {
        this._dataList = _.concat(this._dataList, results);
    }

    getDataVersion() {
        return this._dataVersion;
    }

    getSize() {
        return this.size;
    }

    fetchRange(end) {
        if (this._pending) {
            return;
        }

        this._pending = true;
        return new Promise((resolve) => {
           this.getDataStore(this.job, this.get_url, false, resolve);

        })
        .then((res) => {
            console.log('done loading data store');
            this._pending = false;
            this._end = end;
            this._dataVersion++;
            this.new_last_id = res.last_id;
            this.no_more = res.no_more;
            this.appendResults(res.results);

            this._callback(end);
        });
    }

    getObjectAt(index) {
        if (index >= this._end) {
            this.fetchRange(Math.min(this.size, index + page_size));
            return null;
        }
        if (this._dataList.length > index) {
            return this._dataList[index];
        }
        return null;
    }
}


class RawResultsView extends Component {


    constructor(props) {
        super(props);
        this.updateData = this.updateData.bind(this);
        this.checkExportApiHealth = this.checkExportApiHealth.bind(this);
        this.openExportModal = this.openExportModal.bind(this);
        this.updateWindowDimensions = this.updateWindowDimensions.bind(this);
        this.toggle = this.toggle.bind(this);
        this.toggleAlert = this.toggleAlert.bind(this);
        let final_results = (props.mode === ALL);
        let job_id = props.job.nlp_job_id;
        let get_url = this.props.url + 'phenotype_paged_results/' + job_id + '/' + final_results;
        this.state = {
            ResultData: new ResultData(this.updateData, props.job, get_url),
            end: 0,
            width: 0,
            height: 0,
            mode: props.mode,
            modal: false,
            successAlert: false,
            failureAlert: false,
            alertMessage: "",
            exportApiHealth: false
        };
        this.checkExportApiHealth();
    }

    toggle() {
      this.setState({
        modal: !this.state.modal
      });
    }

    checkExportApiHealth() {
      let __this = this;
      axios.get(process.env.REACT_APP_EXPORT_URL)
      .then(function (response) {
        __this.setState({
          exportApiHealth: true
        });
      })
      .catch(function (error) {
        __this.setState({
          exportApiHealth: false
        });
      });
    }

    componentDidUpdate(prevProps) {
        if (prevProps.mode !== this.props.mode) {

            let final_results = (this.props.mode === ALL);
            let job_id = this.props.job.nlp_job_id;
            let get_url = this.props.url + 'phenotype_paged_results/' + job_id + '/' + final_results;
            this.setState({
                ResultData: new ResultData(this.updateData, this.props.job, get_url),
                mode: this.props.mode
            });
        }
    }

    updateData(end) {
        this.setState({
            end: end
        });
    }

    componentDidMount() {
        this.updateWindowDimensions();
        window.addEventListener('resize', this.updateWindowDimensions);
    }

    componentWillUnmount() {
        this.setState({
            successAlert: false,
            failureAlert: true
        });
        window.removeEventListener('resize', this.updateWindowDimensions);
    }

    updateWindowDimensions() {
        this.setState({
            width: window.innerWidth,
            height: window.innerHeight
        });
    }

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

    openExportModal() {
      this.toggle();
      this.setState({
          successAlert: false,
          failureAlert: false
      });
    }

    // Function to export intermediate results to OMOP database
    exportToOMOP() {
      let __this = this;
      let data = JSON.stringify({
        job_id: this.props.job.nlp_job_id,
        result_name: document.getElementById('omopResultName').value,
        omop_domain: document.getElementById('omopDomain').value,
        concept_id: document.getElementById('omopConceptId').value
      });

      axios.post(process.env.REACT_APP_EXPORT_URL, data, {
        headers: {
            'Content-Type': 'application/json'
        }
      })

      .then(function (response) {
        let data = eval(response);
        let message = data['data'];
        __this.toggleAlert(true);
        __this.setState({
          alertMessage: message
        });
      })
      .catch(function (error) {
        let data = eval(error.response);
        let message = data['data'];
        __this.toggleAlert(false);
        __this.setState({
          alertMessage: message
        });
      });
    }

    populateResultListInModal(result_names) {
      let array = Array.from(result_names);
      let items = [];
      for (let i=0; i<array.length; i++) {
        items.push(<option key={array[i]}>{array[i]}</option>);
      }
      return items;
    }

    render() {
      // iterating over the results to get the unique nlpql_feature names
      let result_names = new Set();
      this.state.ResultData._dataList.forEach(function(resultData) {
        result_names.add(resultData.nlpql_feature);
      });

        const filter_out_columns = ['_id', 'inserted_date', 'phenotype_final', '_id_x', '_id_y', '_id_z'];
        const long_columns = ['sentence', 'sentence_x', 'sentence_y', 'sentence_z'];
        const med_columns = ['term', 'section', 'report_date', 'report_id', 'job_date'];
        let {ResultData, width} = this.state;

        let w = width - 100;
        let columns = ResultData.columns
            .filter(c => filter_out_columns.indexOf(c) < 0)
            .map((c) => {
                let col_width = 75;
                if (long_columns.indexOf(c) >= 0) {
                    col_width = 500;
                } else if (med_columns.indexOf(c) >= 0) {
                    col_width = 200;
                } else if (c.length > 12) {
                    col_width = 200;
                } else if (c.length > 8) {
                    col_width = 150;
                }
            return (
                <Column
                columnKey={c} key={c}
                header={<Cell>{c}</Cell>}
                cell={<PagedCell data={ResultData} />}
                width={col_width}
            />);
        });
        return (
        <div>
          { this.state.ResultData.getSize() > 0 ?
            <div>
                <div className="RawResultsTable">

                    <Table
                        rowHeight={row_height}
                        rowsCount={ResultData.getSize()}
                        headerHeight={header_height}
                        width={w}
                        height={Math.min(600, (ResultData.getSize() * (row_height + 3)) + header_height + 5)}
                        {...this.props}>
                        {columns}
                    </Table>
                    { this.state.ResultData.getSize() > 0 && this.state.exportApiHealth === true?
                    <div className="exportButton">
                      <Button size="lg" onClick={() => { this.openExportModal() }}>Export Results</Button>{' '}
                    </div> :
                    <div></div> }

                    <div id = "exportResultModal">
                      <Modal isOpen={this.state.modal} toggle={this.toggle} className={this.props.className}>
                        <ModalHeader toggle={this.toggle}>Export Results - Job ID: {this.props.job.nlp_job_id}</ModalHeader>
                        <Form>
                        <ModalBody>
                            {this.state.successAlert === true ?
                              <Alert color="success">
                                {this.state.alertMessage}
                              </Alert> :
                              <div></div>
                            }
                            {this.state.failureAlert === true ?
                              <Alert color="danger">
                                {this.state.alertMessage}
                              </Alert> :
                              <div></div>
                            }
                            <FormGroup>
                              <Label for="resultName">Result Name</Label>
                              <Input type="select" name="resultName" id="omopResultName">
                              {this.populateResultListInModal(result_names)}
                              </Input>
                            </FormGroup>
                            <FormGroup>
                              <Label for="conceptId">Concept ID</Label>
                              <Input type="text" name="conceptId" id="omopConceptId" placeholder="Enter Concept ID"/>
                            </FormGroup>
                            <FormGroup>
                              <Label for="domain">OMOP Domain</Label>
                              <Input type="select" name="domain" id="omopDomain">
                                <option>Observation</option>
                                <option>Condition</option>
                                <option>Measurement</option>
                              </Input>
                            </FormGroup>
                        </ModalBody>
                        <ModalFooter>
                          <Button color="primary" onClick={() => { this.exportToOMOP() }}>Export</Button>{' '}
                        </ModalFooter>
                        </Form>
                      </Modal>
                    </div>

                </div>
            </div> :
            <div className="emptyResults">
              No results present.
            </div>
          }
        </div>

        )
    }
}

export default RawResultsView;
