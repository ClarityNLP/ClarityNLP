import { SETTING_LIBRARY } from "./types";

export const setLibrary = () => {
    return {
        type: SETTING_LIBRARY,
        payload: {
            request: {
                url: "library",
                method: "get"
            }
        }
    };
};
