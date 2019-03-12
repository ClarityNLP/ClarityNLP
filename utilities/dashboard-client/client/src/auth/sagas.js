import { USER_EXPIRED, USER_SIGNED_OUT } from "redux-oidc";
import { take } from "redux-saga/effects";
import userManager from "./userManager";

export function* redirectToOIDCSaga() {
    yield take([USER_EXPIRED, USER_SIGNED_OUT]);
    userManager.signinRedirect({
        data: {
            redirectUrl: window.location.href
        }
    });
}
