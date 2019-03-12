import React, { Component } from "react";

const getAnglePoint = (startAngle, endAngle, radius, x, y) => {
    var x1, y1, x2, y2;

    x1 = x + radius * Math.cos((Math.PI * startAngle) / 180);
    y1 = y + radius * Math.sin((Math.PI * startAngle) / 180);
    x2 = x + radius * Math.cos((Math.PI * endAngle) / 180);
    y2 = y + radius * Math.sin((Math.PI * endAngle) / 180);

    return { x1, y1, x2, y2 };
};

export default class Slice extends Component {
    constructor(props) {
        super(props);

        this.state = {
            path: ""
        };
    }

    componentDidMount() {
        this.getPath(0);
    }

    getPath = s => {
        const { angle, startAngle, radius } = this.props;

        let tmp_path = [];
        let a, b;
        let step = angle / (37.5 / 2);

        if (s + step > angle) {
            s = angle;
        }

        // Get angle points
        a = getAnglePoint(startAngle, startAngle + s, radius, radius, radius);
        b = getAnglePoint(startAngle, startAngle + s, 0, radius, radius);

        tmp_path.push("M" + a.x1 + "," + a.y1);

        tmp_path.push(
            "A" +
                radius +
                "," +
                radius +
                " 0 " +
                (s > 180 ? 1 : 0) +
                ",1 " +
                a.x2 +
                "," +
                a.y2
        );

        tmp_path.push("L" + b.x2 + "," + b.y2);

        tmp_path.push(
            "A" +
                0 +
                "," +
                0 +
                " 0 " +
                (s > 180 ? 1 : 0) +
                ",0 " +
                b.x1 +
                "," +
                b.y1
        );

        // Close
        tmp_path.push("Z");

        this.setState({
            path: tmp_path.join(" ")
        });

        if (s < angle) {
            this.getPath(s + step);
        }
    };

    render() {
        const { path } = this.state;
        const { fill } = this.props;

        return (
            <g>
                <path d={path} fill={fill} />
            </g>
        );
    }
}
