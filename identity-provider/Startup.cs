// Copyright (c) Brock Allen & Dominick Baier. All rights reserved.
// Licensed under the Apache License, Version 2.0. See LICENSE in the project root for license information.


using System;
using System.Threading;
using System.Linq;
using System.Reflection;
using System.Security.Cryptography.X509Certificates;
using System.IO;
using IdentityServer4;
using IdentityServer4.EntityFramework.DbContexts;
using IdentityServer4.EntityFramework.Mappers;
using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.HttpOverrides;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Configuration;
using Microsoft.EntityFrameworkCore;
using Microsoft.IdentityModel.Tokens;
using IdentityServer4.Configuration;

namespace IdentityServer
{
    public class Startup
    {
        private readonly ILogger _logger;
        private readonly IConfiguration _config;

        public IHostingEnvironment Environment { get; }

        public Startup(IHostingEnvironment environment, ILogger<Startup> logger, IConfiguration config)
        {
            Environment = environment;
            StaticConfig = config;
            _config = config;
            _logger = logger;
        }

        public static IConfiguration StaticConfig { get; private set; }

        public void ConfigureServices(IServiceCollection services)
        {
            services.AddMvc().SetCompatibilityVersion(Microsoft.AspNetCore.Mvc.CompatibilityVersion.Version_2_1);

            var connectionString = $@"Data Source=mssql;database={_config["IDP_DATABASE"]};User=sa;Password={_config["IDP_DB_PASSWORD"]};trusted_connection=false;";
            var migrationsAssembly = typeof(Startup).GetTypeInfo().Assembly.GetName().Name;

            var builder = services.AddIdentityServer(options =>
                {
                    options.PublicOrigin = $"{_config["PROTOCOL"]}://{_config["IDP_URL"]}";
                })
                .AddTestUsers(Config.GetUsers());
            if (Environment.IsDevelopment())
            {
                builder.AddInMemoryIdentityResources(Config.GetIdentityResources())
                .AddInMemoryApiResources(Config.GetApis())
                .AddInMemoryClients(Config.GetClients())
                .AddDeveloperSigningCredential();
            }
            else
            {
                if (!File.Exists("/app/creds/idp.pfx"))
                {
                    throw new FileNotFoundException("Signing Certificate is missing!");
                }

                var cert = new X509Certificate2("/app/creds/idp.pfx", _config["IDP_SIGNING_CREDS_PASSPHRASE"]);
                // this adds the config data from DB (clients, resources)
                builder.AddConfigurationStore(options =>
                {
                    options.ConfigureDbContext = b =>
                        b.UseSqlServer(connectionString,
                            sql =>
                            {
                                sql.MigrationsAssembly(migrationsAssembly);
                            });
                })
                // this adds the operational data from DB (codes, tokens, consents)
                .AddOperationalStore(options =>
                {
                    options.ConfigureDbContext = b =>
                        b.UseSqlServer(connectionString,
                            sql =>
                            {
                                sql.MigrationsAssembly(migrationsAssembly);
                            });
                    // this enables automatic token cleanup. this is optional.
                    options.EnableTokenCleanup = true;
                })
                // .AddDeveloperSigningCredential();
                .AddSigningCredential(cert);
            }
        }

        public void Configure(IApplicationBuilder app)
        {
            if (Environment.IsDevelopment())
            {
                _logger.LogInformation("In Development environment.");
                app.UseDeveloperExceptionPage();
            }
            else {
                _logger.LogInformation("In Production environment.");
                // this will do the initial DB population
                InitializeDatabase(app);
            }

            var fordwardedHeaderOptions = new ForwardedHeadersOptions
            {
                ForwardedHeaders = ForwardedHeaders.XForwardedFor | ForwardedHeaders.XForwardedProto
            };
            fordwardedHeaderOptions.KnownNetworks.Clear();
            fordwardedHeaderOptions.KnownProxies.Clear();

            app.UseForwardedHeaders(fordwardedHeaderOptions);

            app.UseStaticFiles();

            app.UseIdentityServer();

            app.UseMvcWithDefaultRoute();
        }

        private void InitializeDatabase(IApplicationBuilder app)
        {
            using (var serviceScope = app.ApplicationServices.GetService<IServiceScopeFactory>().CreateScope())
            {
                serviceScope.ServiceProvider.GetRequiredService<PersistedGrantDbContext>().Database.Migrate();

                var context = serviceScope.ServiceProvider.GetRequiredService<ConfigurationDbContext>();
                context.Database.Migrate();
                if (!context.Clients.Any())
                {
                    foreach (var client in Config.GetClients())
                    {
                        context.Clients.Add(client.ToEntity());
                    }
                    context.SaveChanges();
                }

                if (!context.IdentityResources.Any())
                {
                    foreach (var resource in Config.GetIdentityResources())
                    {
                        context.IdentityResources.Add(resource.ToEntity());
                    }
                    context.SaveChanges();
                }

                if (!context.ApiResources.Any())
                {
                    foreach (var resource in Config.GetApis())
                    {
                        context.ApiResources.Add(resource.ToEntity());
                    }
                    context.SaveChanges();
                }
            }
        }
    }
}
