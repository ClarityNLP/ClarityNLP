FROM microsoft/dotnet:2.2-sdk AS build-env
WORKDIR /app

# Copy csproj and restore as distinct layers
COPY *.csproj ./

RUN dotnet restore

# Copy everything else and build
COPY . ./

RUN dotnet publish -c Release -o out

#Build runtime image
FROM microsoft/dotnet:2.2.1-aspnetcore-runtime
WORKDIR /app
COPY --from=build-env /app/out .
COPY --from=build-env /app/wait-for-it-extra.sh .

COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh
RUN ln -s usr/local/bin/docker-entrypoint.sh / # backwards compat

EXPOSE 5000

ENTRYPOINT ["docker-entrypoint.sh"]

CMD ["dotnet", "IdentityServer.dll"]
