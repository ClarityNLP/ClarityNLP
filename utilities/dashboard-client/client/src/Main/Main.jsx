import React, { Component } from "react";
import Navbar from "./Navbar";
import Documents from "./Documents";
import Library from "./Library";
import Results from "./Results";

export default class Main extends Component {
    componentDidMount() {
        this.props.setDocuments();
        this.props.setJobs();
        this.props.setLibrary();

        // setInterval(() => {
        //     this.props.setDocuments();
        //     this.props.setJobs();
        // }, 5000);
    }

    render() {
        return (
            <React.Fragment>
                <Navbar />
                <div className="dashboard_container">
                    <div className="columns dashboard_columns">
                        <div className="column dashboard_column">
                            <Documents />
                            <Library />
                        </div>
                        <div className="column dashboard_column">
                            <Results />
                        </div>
                    </div>
                </div>
            </React.Fragment>
        );
    }
}
