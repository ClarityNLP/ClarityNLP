import { SETTING_DOCUMENTS } from "./types";

export const setDocuments = () => {
    return {
        type: SETTING_DOCUMENTS,
        payload: {
            request: {
                url: "document_sources",
                method: "get"
            }
        }
    };
};
