import React, { Component } from "react";
import Slice from "./Slice";

export default class PieChart extends Component {
    constructor(props) {
        super(props);

        this.state = {
            sum: 0,
            slices: [],
            legend: []
        };
    }

    componentDidUpdate(prevProps) {
        const { data } = this.props;

        if (data !== prevProps.data) {
            const tmp_sum = data
                .map(s => {
                    return s.value;
                })
                .reduce((carry, current) => {
                    return carry + current;
                }, 0);

            this.setState(
                {
                    sum: tmp_sum
                },
                this.getSlices
            );
        }
    }

    getSlices = () => {
        const { sum } = this.state;
        const { data, radius } = this.props;
        let startAngle = 0;
        let tmp_slices = [];

        if (data.length > 1) {
            for (let index in data) {
                const slice = data[index];
                const { value, color } = slice;
                let angle, nextAngle;

                nextAngle = startAngle;
                angle = (value / sum) * 360;
                startAngle += angle;

                tmp_slices.push(
                    <Slice
                        key={"slice" + index}
                        radius={radius}
                        startAngle={nextAngle}
                        angle={angle}
                        fill={color}
                    />
                );
            }
        } else {
            tmp_slices.push(
                <circle
                    cx={radius}
                    cy={radius}
                    r={radius}
                    fill={data[0].color}
                />
            );
        }

        this.setState(
            {
                slices: tmp_slices
            },
            this.getLegend
        );
    };

    getLegend = () => {
        const { data } = this.props;
        let tmp_legend = [];

        tmp_legend = data.map((key, i) => {
            const { value, color, label } = key;

            return (
                <tr key={"legend" + i}>
                    <td style={{ backgroundColor: color }} />
                    <td>{label}</td>
                    <td>{value}</td>
                </tr>
            );
        });

        this.setState({
            legend: tmp_legend
        });
    };

    render() {
        const { slices, legend } = this.state;
        const diameter = 200;

        return (
            <div className="columns card_columns">
                <div className="column is-half is-narrow">
                    <svg
                        width={diameter}
                        height={diameter}
                        viewBox={"0 0 " + diameter + " " + diameter}
                        xmlns="http://www.w3.org/2000/svg"
                        version="1.1"
                    >
                        {slices}
                    </svg>
                </div>
                <div className="column is-half is-narrow">
                    <div className="pie_legend">
                        <table className="table is-narrow is-fullwidth">
                            <tbody>{legend}</tbody>
                        </table>
                    </div>
                </div>
            </div>
        );
    }
}
