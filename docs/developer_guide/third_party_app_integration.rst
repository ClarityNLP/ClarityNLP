Third Party App Integration
===========================

The information below will help you configure a third-party application for ClarityNLP.

By "third-party", we are referring to applications not developed by the core ClarityNLP team. The third-party app would like access to your ClarityNLP's resources.

The third-party application must be a registered OAuth2 Client with ClarityNLP's Identity Provider in order to complete an OAuth2 Flow and be issued an access token.

If you need a refresher on OAuth2 in order to determine the ideal Grant Type for the third-party application, `here is a review <https://www.digitalocean.com/community/tutorials/an-introduction-to-oauth-2>`_.

Once you have determined the appropriate Grand Type, refer to :code:`/identity-provider/Config.cs` to see examples of how to configure your client.

An exhaustive list of Client properties can be found `here <http://docs.identityserver.io/en/latest/reference/client.html>`_.


