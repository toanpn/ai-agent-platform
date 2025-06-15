FROM mcr.microsoft.com/dotnet/aspnet:8.0 AS base
WORKDIR /app
EXPOSE 80

FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src
COPY ["AgentPlatform.API/AgentPlatform.API.csproj", "AgentPlatform.API/"]
COPY ["shared/AgentPlatform.Shared.csproj", "shared/"]
RUN dotnet restore "AgentPlatform.API/AgentPlatform.API.csproj"
COPY AgentPlatform.API/ AgentPlatform.API/
COPY shared/ shared/
WORKDIR "/src/AgentPlatform.API"
RUN dotnet build "AgentPlatform.API.csproj" -c Release -o /app/build

FROM build AS publish
RUN dotnet publish "AgentPlatform.API.csproj" -c Release -o /app/publish

FROM base AS final
WORKDIR /app
COPY --from=publish /app/publish .
ENTRYPOINT ["dotnet", "AgentPlatform.API.dll"] 