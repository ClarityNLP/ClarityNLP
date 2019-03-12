import { RUNNING_NLPQL } from "./types";
import axios from "axios";

export const runNLPQL = nlpql => dispatch => {
    const url = process.env.REACT_APP_CLARITY_API_URL + "nlpql";

    axios.post(url, nlpql).then(() => {
        dispatch({
            type: RUNNING_NLPQL
        });
    });
};
