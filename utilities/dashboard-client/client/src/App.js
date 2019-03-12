import React from "react";
import { Provider } from "react-redux";
import userManager from "./auth/userManager";
import { OidcProvider } from "redux-oidc";
import { Route } from "react-router-dom";
import { ConnectedRouter } from "connected-react-router";
import Main from "./Main";

const App = ({ store, history }) => (
    <Provider store={store}>
        <OidcProvider store={store} userManager={userManager}>
            <ConnectedRouter history={history}>
                <Route path="" component={Main} />
            </ConnectedRouter>
        </OidcProvider>
    </Provider>
);

export default App;
