import { connect } from "react-redux";
import Documents from "./Documents";

function mapStateToProps(state) {
    return {
        app: state.app
    };
}

const DocumentsContainer = connect(
    mapStateToProps,
    {}
)(Documents);

export default DocumentsContainer;
