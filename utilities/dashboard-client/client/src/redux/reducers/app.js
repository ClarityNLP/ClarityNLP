import * as types from "../actions/types";

const initialState = {
    documents: [],
    documents_loading: false,
    documents_error: {},
    jobs: [],
    jobs_loading: false,
    jobs_error: {},
    library: [],
    library_loading: false,
    library_error: {},
    running_nlpql: false
};

const reducer = (state = initialState, action) => {
    switch (action.type) {
        case types.SETTING_DOCUMENTS:
            return {
                ...state,
                documents_loading: true
            };
        case types.SETTING_DOCUMENTS_SUCCESS:
            return {
                ...state,
                documents_loading: false,
                documents: action.payload.data.facet_counts.facet_fields.source.slice(
                    0,
                    10
                )
            };
        case types.SETTING_DOCUMENTS_FAIL:
            return {
                ...state,
                documents_loading: false,
                documents_error: action.payload.data
            };
        case types.SETTING_JOBS:
            return {
                ...state,
                jobs_loading: true
            };
        case types.SETTING_JOBS_SUCCESS:
            return {
                ...state,
                jobs_loading: false,
                jobs: action.payload.data
            };
        case types.SETTING_JOBS_FAIL:
            return {
                ...state,
                jobs_loading: false,
                jobs_error: action.payload.data
            };
        case types.SETTING_LIBRARY:
            return {
                ...state,
                library_loading: true
            };
        case types.SETTING_LIBRARY_SUCCESS:
            return {
                ...state,
                library_loading: false,
                library: action.payload.data
            };
        case types.SETTING_LIBRARY_FAIL:
            return {
                ...state,
                library_loading: false,
                libary_error: action.payload.data
            };
        case types.RUNNING_NLPQL:
            return {
                ...state,
                running_nlpql: true
            };
        case types.RUNNING_NLPQL_SUCCESS:
            return {
                ...state,
                running_nlpql: false
            };
        case types.RUNNING_NLPQL_FAIL:
            return {
                ...state,
                running_nlpql: false
            };
        default:
            return state;
    }
};

export { reducer };
