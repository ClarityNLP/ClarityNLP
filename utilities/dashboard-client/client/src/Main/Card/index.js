import React, { Component } from "react";
import { FaExpand, FaCompress } from "react-icons/fa";

export default class Card extends Component {
    constructor(props) {
        super(props);

        this.state = {
            toggle: false
        };
    }

    toggle = () => {
        this.setState(state => ({
            toggle: !state.toggle
        }));
    };

    render() {
        const { className, heading, cta_label, cta_href } = this.props;
        const { toggle } = this.state;

        return (
            <div
                className={
                    toggle
                        ? "card-container expanded " + className
                        : "card-container " + className
                }
            >
                <div className="card">
                    <header className="card-header">
                        <p className="card-header-title">{heading}</p>
                        <button
                            className="card-header-icon expand_button"
                            onClick={this.toggle}
                        >
                            {toggle ? <FaCompress /> : <FaExpand />}
                        </button>
                    </header>
                    <div className="card-content">{this.props.children}</div>
                    <div className="card-footer">
                        <div
                            className={
                                toggle
                                    ? "column is-2 is-offset-10"
                                    : "column is-4 is-offset-8"
                            }
                        >
                            <a
                                href={cta_href}
                                className="button is-primary is-fullwidth"
                            >
                                {cta_label}
                            </a>
                        </div>
                    </div>
                </div>
            </div>
        );
    }
}
