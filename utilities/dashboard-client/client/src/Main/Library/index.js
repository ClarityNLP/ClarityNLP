import { connect } from "react-redux";
import Library from "./Library";
import { runNLPQL } from "../../redux/actions/run_nlpql";

function mapStateToProps(state) {
    return {
        app: state.app
    };
}

const LibraryContainer = connect(
    mapStateToProps,
    { runNLPQL }
)(Library);

export default LibraryContainer;
