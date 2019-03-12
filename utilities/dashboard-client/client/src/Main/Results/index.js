import { connect } from "react-redux";
import Results from "./Results";

function mapStateToProps(state) {
    return {
        app: state.app
    };
}

const ResultsContainer = connect(
    mapStateToProps,
    {}
)(Results);

export default ResultsContainer;
