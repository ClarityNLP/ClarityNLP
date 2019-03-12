import { applyMiddleware, compose, createStore } from "redux";
import axiosMiddleware from "redux-axios-middleware";
import { routerMiddleware } from "connected-react-router";
import createRootReducer from "../reducers/root_reducer";

// MIDDLEWARES
import thunk from "redux-thunk";
import { createLogger } from "redux-logger";
import createSagaMiddleware from "redux-saga";
import { redirectToOIDCSaga } from "../../auth/sagas";

const logger = createLogger();
const sagaMiddleware = createSagaMiddleware();

export default function configureStore(initialState, apiClient, history) {
    const store = createStore(
        createRootReducer(history),
        initialState,
        compose(
            applyMiddleware(
                sagaMiddleware,
                routerMiddleware(history),
                thunk,
                axiosMiddleware(apiClient),
                logger
            )
        )
    );

    sagaMiddleware.run(redirectToOIDCSaga);

    return store;
}
