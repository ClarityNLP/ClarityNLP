// Copyright (c) Brock Allen & Dominick Baier. All rights reserved.
// Licensed under the Apache License, Version 2.0. See LICENSE in the project root for license information.


using IdentityServer4;
using IdentityServer4.Models;
using IdentityServer4.Test;
using System.Collections.Generic;
using System.Security.Claims;

namespace IdentityServer
{
    public static class Config
    {
        public static List<TestUser> GetUsers()
        {
            return new List<TestUser>
            {
                new TestUser
                {
                    SubjectId = "1",
                    Username = "admin",
                    Password = "admin",

                    Claims = new []
                    {
                        new Claim("name", "Admin"),
                        new Claim("website", "https://www.hdap.gatech.edu")
                    }
                }
            };
        }

        public static IEnumerable<IdentityResource> GetIdentityResources()
        {
            return new List<IdentityResource>
            {
                new IdentityResources.OpenId(),
                new IdentityResources.Profile(),
            };
        }

        public static IEnumerable<ApiResource> GetApis()
        {
            return new List<ApiResource>
            {
              new ApiResource
              {
                Name = "ingest_api",
                DisplayName = "Ingest API",
                ApiSecrets =
                {
                    new Secret("secret".Sha256())
                },
                Scopes =
                {
                    new Scope()
                    {
                        Name = "ingest_api",
                        DisplayName = "Ingest API"
                    }
                }
              },
              new ApiResource
              {
                Name = "solr_api",
                DisplayName = "Solr API",
                ApiSecrets =
                {
                    new Secret("secret".Sha256())
                },
                Scopes =
                {
                    new Scope()
                    {
                        Name = "solr_api",
                        DisplayName = "Solr API"
                    }
                }
              },
              new ApiResource
              {
                Name = "nlp_api",
                DisplayName = "NLP API",
                ApiSecrets =
                {
                    new Secret("secret".Sha256())
                },
                Scopes =
                {
                    new Scope()
                    {
                        Name = "nlp_api",
                        DisplayName = "NLP API"
                    }
                }
              }
            };
        }

        public static IEnumerable<Client> GetClients()
        {
            return new List<Client>
            {
                new Client
                {
                    ClientId = "client",

                    // no interactive user, use the clientid/secret for authentication
                    AllowedGrantTypes = GrantTypes.ClientCredentials,

                    // secret for authentication
                    ClientSecrets =
                    {
                        new Secret("secret".Sha256())
                    },

                    // scopes that client has access to
                    AllowedScopes = { "api1" }
                },
                // resource owner password grant client
                new Client
                {
                    ClientId = "ro.client",
                    AllowedGrantTypes = GrantTypes.ResourceOwnerPassword,

                    ClientSecrets =
                    {
                        new Secret("secret".Sha256())
                    },
                    AllowedScopes = { "api1" }
                },
                // OpenID Connect hybrid flow client (MVC)
                new Client
                {
                    ClientId = "mvc",
                    ClientName = "MVC Client",
                    AllowedGrantTypes = GrantTypes.Hybrid,

                    ClientSecrets =
                    {
                        new Secret("secret".Sha256())
                    },

                    RedirectUris           = { "http://localhost:5002/signin-oidc" },
                    PostLogoutRedirectUris = { "http://localhost:5002/signout-callback-oidc" },

                    AllowedScopes =
                    {
                        IdentityServerConstants.StandardScopes.OpenId,
                        IdentityServerConstants.StandardScopes.Profile,
                        "api1"
                    },

                    AllowOfflineAccess = true
                },
                // SPA - Ingest Client
                new Client
                {
                    ClientId = "ingest",
                    ClientName = "Ingest",
                    AllowedGrantTypes = GrantTypes.Code,
                    RequirePkce = true,
                    RequireClientSecret = false,
                    RedirectUris =           { "https://ingest.claritynlp.dev/silent_renew.html", "https://ingest.claritynlp.dev/callback.html" },
                    PostLogoutRedirectUris = { "https://ingest.claritynlp.dev/csv" },
                    AllowedCorsOrigins =     { "https://ingest.claritynlp.dev" },
                    AllowedScopes =
                    {
                        IdentityServerConstants.StandardScopes.OpenId,
                        IdentityServerConstants.StandardScopes.Profile,
                        "ingest_api",
                        "solr_api"
                    }
                },
                // SPA - Results Viewer Client
                new Client
                {
                    ClientId = "viewer",
                    ClientName = "Results Viewer",
                    AllowedGrantTypes = GrantTypes.Code,
                    RequirePkce = true,
                    RequireClientSecret = false,
                    RedirectUris =           { "https://viewer.claritynlp.dev/silent_renew.html", "https://viewer.claritynlp.dev/callback.html" },
                    PostLogoutRedirectUris = { "https://viewer.claritynlp.dev" },
                    AllowedCorsOrigins =     { "https://viewer.claritynlp.dev" },
                    AllowedScopes =
                    {
                        IdentityServerConstants.StandardScopes.OpenId,
                        IdentityServerConstants.StandardScopes.Profile,
                        "nlp_api"
                    }
                },
                // SPA - Dashboard Client
                new Client
                {
                    ClientId = "dashboard",
                    ClientName = "Dashboard",
                    AllowedGrantTypes = GrantTypes.Code,
                    RequirePkce = true,
                    RequireClientSecret = false,
                    RedirectUris =           { "https://dashboard.claritynlp.dev/silent_renew.html", "https://dashboard.claritynlp.dev/callback.html" },
                    PostLogoutRedirectUris = { "https://dashboard.claritynlp.dev" },
                    AllowedCorsOrigins =     { "https://dashboard.claritynlp.dev" },
                    AllowedScopes =
                    {
                        IdentityServerConstants.StandardScopes.OpenId,
                        IdentityServerConstants.StandardScopes.Profile,
                        "nlp_api",
                        "solr_api"
                    }
                },
                // SPA - Redux OIDC Example App
                new Client
                {
                    ClientId = "redux_test",
                    ClientName = "Redux Test Client",
                    AllowedGrantTypes = GrantTypes.Code,
                    RequirePkce = true,
                    RequireClientSecret = false,

                    // RedirectUris =           { "http://localhost:5003/callback.html", "http://localhost:5003/silent.html" },
                    RedirectUris =           { "http://localhost:9090/silent_renew.html", "http://localhost:9090/callback" },
                    PostLogoutRedirectUris = { "http://localhost:9090" },
                    AllowedCorsOrigins =     { "http://localhost:9090" },

                    AllowedScopes =
                    {
                        IdentityServerConstants.StandardScopes.OpenId,
                        IdentityServerConstants.StandardScopes.Profile,
                        "api1"
                    }
                },
                // JavaScript Client #1
                new Client
                {
                    ClientId = "js",
                    ClientName = "JavaScript Client",
                    AllowedGrantTypes = GrantTypes.Code,
                    RequirePkce = true,
                    RequireClientSecret = false,

                    // RedirectUris =           { "http://localhost:5003/callback.html", "http://localhost:5003/silent.html" },
                    RedirectUris =           { "http://localhost:5003/silent_renew.html", "http://localhost:5003/callback" },
                    PostLogoutRedirectUris = { "http://localhost:5003/index.html" },
                    AllowedCorsOrigins =     { "http://localhost:5003" },

                    AllowedScopes =
                    {
                        IdentityServerConstants.StandardScopes.OpenId,
                        IdentityServerConstants.StandardScopes.Profile,
                        "api1"
                    }
                },
                // JavaScript Client #2
                new Client
                {
                    ClientId = "js2",
                    ClientName = "JavaScript Client",
                    AllowedGrantTypes = GrantTypes.Code,
                    RequirePkce = true,
                    RequireClientSecret = false,

                    RedirectUris =           { "http://localhost:5004/callback.html", "http://localhost:5004/silent.html" },
                    // RedirectUris =           { "http://localhost:5003/callback" },
                    PostLogoutRedirectUris = { "http://localhost:5004/index.html" },
                    AllowedCorsOrigins =     { "http://localhost:5004" },

                    AllowedScopes =
                    {
                        IdentityServerConstants.StandardScopes.OpenId,
                        IdentityServerConstants.StandardScopes.Profile,
                        "api1"
                    }
                },
                // ORY Oathkeeper (Client Credentials)
                new Client
                {
                    ClientId = "api1",

                    // no interactive user, use the clientid/secret for authentication
                    AllowedGrantTypes = GrantTypes.ClientCredentials,

                    // secret for authentication
                    ClientSecrets =
                    {
                        new Secret("secret".Sha256())
                    },

                    // scopes that client has access to
                    // AllowedScopes = { "api1" }
                }
            };
        }
    }
}
