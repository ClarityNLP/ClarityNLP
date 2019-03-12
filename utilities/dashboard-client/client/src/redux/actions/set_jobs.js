import { SETTING_JOBS } from "./types";

export const setJobs = () => {
    return {
        type: SETTING_JOBS,
        payload: {
            request: {
                url: "jobs",
                method: "get"
            }
        }
    };
};
