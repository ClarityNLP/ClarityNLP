// Copyright (c) Brock Allen & Dominick Baier. All rights reserved.
// Licensed under the Apache License, Version 2.0. See LICENSE in the project root for license information.


using IdentityServer4;
using IdentityServer4.Models;
using IdentityServer4.Test;
using System.Collections.Generic;
using System.Security.Claims;
using Microsoft.Extensions.Configuration;
using IdentityServer4.Configuration;

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
                    Username = $"{Startup.StaticConfig["ADMIN_USERNAME"]}",
                    Password = $"{Startup.StaticConfig["ADMIN_PASSWORD"]}",

                    Claims = new []
                    {
                        new Claim("name", "Admin"),
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
                    ClientId = "formbuilder",
                    AllowedGrantTypes = GrantTypes.ClientCredentials,
                    ClientSecrets =
                    {
                        new Secret(Startup.StaticConfig["CLIENT_FORMBUILDER_SECRET"].Sha256())
                    },
                    AccessTokenLifetime = 3000000,
                    AllowedScopes =
                    {
                        "nlpaas"
                    }
                },
                new Client
                {
                    ClientId = "nlpass",
                    AllowedGrantTypes = GrantTypes.ClientCredentials,
                    ClientSecrets =
                    {
                        new Secret(Startup.StaticConfig["CLIENT_NLPASS_SECRET"].Sha256())
                    },
                    AccessTokenLifetime = 3000000,
                    AllowedScopes =
                    {
                        "solr_api",
                        "nlp_api"
                    }
                },
                new Client
                {
                    ClientId = "cli",
                    AllowedGrantTypes = GrantTypes.ClientCredentials,
                    ClientSecrets =
                    {
                        new Secret(Startup.StaticConfig["CLIENT_CLI_SECRET"].Sha256())
                    },
                    AccessTokenLifetime = 3000000,
                    AllowedScopes =
                    {
                        "ingest_api",
                        "solr_api",
                        "nlp_api"
                    }
                },
                new Client
                {
                    ClientId = "ingest",
                    ClientName = "Ingest",
                    RequireConsent = false,
                    AllowedGrantTypes = GrantTypes.Code,
                    RequirePkce = true,
                    RequireClientSecret = false,
                    RedirectUris =
                    {
                        $"{Startup.StaticConfig["PROTOCOL"]}://{Startup.StaticConfig["INGEST_URL"]}/silent_renew.html",
                        $"{Startup.StaticConfig["PROTOCOL"]}://{Startup.StaticConfig["INGEST_URL"]}/callback.html"
                    },
                    PostLogoutRedirectUris =
                    {
                        $"{Startup.StaticConfig["PROTOCOL"]}://{Startup.StaticConfig["INGEST_URL"]}/csv"
                    },
                    AllowedCorsOrigins =
                    {
                        $"{Startup.StaticConfig["PROTOCOL"]}://{Startup.StaticConfig["HOST"]}"
                    },
                    AllowedScopes =
                    {
                        IdentityServerConstants.StandardScopes.OpenId,
                        IdentityServerConstants.StandardScopes.Profile,
                        "ingest_api",
                        "solr_api"
                    }
                },
                new Client
                {
                    ClientId = "viewer",
                    ClientName = "Results Viewer",
                    RequireConsent = false,
                    AllowedGrantTypes = GrantTypes.Code,
                    RequirePkce = true,
                    RequireClientSecret = false,
                    RedirectUris =
                    {
                        $"{Startup.StaticConfig["PROTOCOL"]}://{Startup.StaticConfig["RESULTS_URL"]}/silent_renew.html",
                        $"{Startup.StaticConfig["PROTOCOL"]}://{Startup.StaticConfig["RESULTS_URL"]}/callback.html"
                    },
                    PostLogoutRedirectUris =
                    {
                        $"{Startup.StaticConfig["PROTOCOL"]}://{Startup.StaticConfig["RESULTS_URL"]}"
                    },
                    AllowedCorsOrigins =
                    {
                        $"{Startup.StaticConfig["PROTOCOL"]}://{Startup.StaticConfig["HOST"]}"
                    },
                    AllowedScopes =
                    {
                        IdentityServerConstants.StandardScopes.OpenId,
                        IdentityServerConstants.StandardScopes.Profile,
                        "nlp_api"
                    }
                },
                new Client
                {
                    ClientId = "dashboard",
                    ClientName = "Dashboard",
                    RequireConsent = false,
                    AllowedGrantTypes = GrantTypes.Code,
                    RequirePkce = true,
                    RequireClientSecret = false,
                    RedirectUris =
                    {
                        $"{Startup.StaticConfig["PROTOCOL"]}://{Startup.StaticConfig["DASHBOARD_URL"]}/silent_renew.html",
                        $"{Startup.StaticConfig["PROTOCOL"]}://{Startup.StaticConfig["DASHBOARD_URL"]}/callback.html"
                    },
                    PostLogoutRedirectUris =
                    {
                        $"{Startup.StaticConfig["PROTOCOL"]}://{Startup.StaticConfig["DASHBOARD_URL"]}"
                    },
                    AllowedCorsOrigins =
                    {
                        $"{Startup.StaticConfig["PROTOCOL"]}://{Startup.StaticConfig["HOST"]}"
                    },
                    AllowedScopes =
                    {
                        IdentityServerConstants.StandardScopes.OpenId,
                        IdentityServerConstants.StandardScopes.Profile,
                        "nlp_api",
                        "solr_api"
                    }
                }
            };
        }
    }
}
