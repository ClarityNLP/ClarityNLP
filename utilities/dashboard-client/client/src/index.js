import React from "react";
import ReactDOM from "react-dom";
import axios from "axios";
import { loadUser } from "redux-oidc";
import userManager from "./auth/userManager";
import configureStore from "./redux/store/store";
import { createBrowserHistory } from "history";
import App from "./App";
import * as serviceWorker from "./serviceWorker";
import "./styles/style.scss";

serviceWorker.register();

const history = createBrowserHistory();

const initialState = {};

const apiClient = axios.create({
    baseURL: process.env.REACT_APP_API_URL,
    responseType: "text"
});

const store = configureStore(initialState, apiClient, history);

loadUser(store, userManager);

ReactDOM.render(
    <App store={store} history={history} />,
    document.getElementById("root")
);
