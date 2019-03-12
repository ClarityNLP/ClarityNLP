import React, { Component } from "react";
import Card from "../Card";
import { FaPlay } from "react-icons/fa";

export default class Library extends Component {
    constructor(props) {
        super(props);

        this.state = {
            library_data: []
        };
    }

    componentDidUpdate(prevProps) {
        if (prevProps.app.library !== this.props.app.library) {
            this.setContent();
        }
    }

    setContent = () => {
        const { library } = this.props.app;

        let data = [];

        data = library.map((query, i) => {
            return (
                <tr key={"query" + i} className="query_row">
                    <td>{query.nlpql_name}</td>
                    <td
                        className="run_button has-text-right"
                        onClick={() => {
                            this.props.runNLPQL(query.nlpql_raw);
                        }}
                    >
                        <FaPlay />
                    </td>
                </tr>
            );
        });

        this.setState({
            library_data: data
        });
    };

    render() {
        const { library_data } = this.state;

        return (
            <Card
                className="library"
                heading="Query Library"
                cta_label="Add Query"
                cta_href={process.env.REACT_APP_QUERY_BUILDER_URL}
            >
                <div className="library_container">
                    <table className="table is-fullwidth is-striped is-fullwidth">
                        <tbody>{library_data}</tbody>
                    </table>
                </div>
            </Card>
        );
    }
}
