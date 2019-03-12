import React, { Component } from "react";
import { FaCubes, FaPoll, FaFolder, FaChartBar, FaCog } from "react-icons/fa";

export default class Navbar extends Component {
    render() {
        const {
            REACT_APP_RESULT_VIEWER_URL,
            REACT_APP_INGEST_URL,
            REACT_APP_QUERY_BUILDER_URL
        } = process.env;

        return (
            <React.Fragment>
                <nav className="top_nav navbar">
                    <div className="navbar-brand">
                        <div className="navbar-item">
                            <h4 className="is-size-4">ClarityNLP</h4>
                        </div>
                    </div>
                    <div className="navbar-menu">
                        <div className="navbar-start" />
                        <div className="navbar-end">
                            <div className="navbar-item">
                                <a href="/">
                                    <FaCog />
                                </a>
                            </div>
                        </div>
                    </div>
                </nav>
                <nav className="side_nav">
                    <div className="nav-links">
                        <a
                            href="/"
                            className="nav-link has-text-centered active"
                        >
                            <span className="link-icon is-size-4">
                                <FaPoll />
                            </span>
                            Dashboard
                        </a>
                        <a
                            href={REACT_APP_INGEST_URL}
                            className="nav-link has-text-centered"
                        >
                            <span className="link-icon is-size-4">
                                <FaFolder />
                            </span>
                            Documents
                        </a>
                        <a
                            href={REACT_APP_QUERY_BUILDER_URL}
                            className="nav-link has-text-centered"
                        >
                            <span className="link-icon is-size-4">
                                <FaCubes />
                            </span>
                            Query Builder
                        </a>
                        <a
                            href={REACT_APP_RESULT_VIEWER_URL}
                            className="nav-link has-text-centered"
                        >
                            <span className="link-icon is-size-4">
                                <FaChartBar />
                            </span>
                            Results
                        </a>
                    </div>
                </nav>
            </React.Fragment>
        );
    }
}
