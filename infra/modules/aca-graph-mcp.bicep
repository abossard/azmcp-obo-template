@description('Location for all resources')
param location string = resourceGroup().location

@description('Default name for Graph MCP Server Container App')
param name string

@description('Container App name for Graph MCP Server')
param containerAppName string = '${name}-graph'

@description('Environment name for the Container Apps Environment')
param environmentName string

@description('Number of CPU cores allocated to the container')
param cpuCores string = '0.25'

@description('Amount of memory allocated to the container')
param memorySize string = '0.5Gi'

@description('Minimum number of replicas')
param minReplicas int = 1

@description('Maximum number of replicas')
param maxReplicas int = 3

@description('Application Insights connection string')
param appInsightsConnectionString string

@description('Azure AD Tenant ID')
param azureAdTenantId string

@description('Azure AD Client ID')
param azureAdClientId string

@description('Azure AD authorization Server')
param azureAdInstance string

@description('Resource ID of the user-assigned managed identity')
param userAssignedManagedIdentityId string = ''

@description('Client ID of the user-assigned managed identity')
param userAssignedManagedIdentityClientId string = ''

@description('Container registry for custom image')
param containerRegistry string = 'mcr.microsoft.com'

@description('Container image for Graph MCP Server')
param containerImage string = 'graph-mail-mcp-server:latest'

// Use existing Container Apps Environment
resource containerAppsEnvironment 'Microsoft.App/managedEnvironments@2024-03-01' existing = {
  name: environmentName
}

resource containerApp 'Microsoft.App/containerApps@2024-03-01' = {
  name: containerAppName
  location: location
  tags: {
    product: 'graph-mcp'
  }
  identity: !empty(userAssignedManagedIdentityId) ? {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${userAssignedManagedIdentityId}': {}
    }
  } : null
  properties: {
    managedEnvironmentId: containerAppsEnvironment.id
    configuration: {
      activeRevisionsMode: 'Single'
      ingress: {
        external: true
        targetPort: 8080
        allowInsecure: false
        transport: 'http'
        traffic: [
          {
            weight: 100
            latestRevision: true
          }
        ]
      }
    }
    template: {
      containers: [
        {
          name: 'graph-mail-mcp-server'
          image: '${containerRegistry}/${containerImage}'
          resources: {
            cpu: json(cpuCores)
            memory: memorySize
          }
          env: [
            {
              name: 'AZURE_AD_TENANT_ID'
              value: azureAdTenantId
            }
            {
              name: 'AZURE_AD_CLIENT_ID'
              value: azureAdClientId
            }
            {
              name: 'AZURE_AD_INSTANCE'
              value: azureAdInstance
            }
            {
              name: 'AZURE_CLIENT_ID'
              value: userAssignedManagedIdentityClientId
            }
            {
              name: 'APPLICATIONINSIGHTS_CONNECTION_STRING'
              value: appInsightsConnectionString
            }
          ]
        }
      ]
      scale: {
        minReplicas: minReplicas
        maxReplicas: maxReplicas
        rules: [
          {
            name: 'http-scaling-rule'
            http: {
              metadata: {
                concurrentRequests: '10'
              }
            }
          }
        ]
      }
    }
  }
}

output containerAppUrl string = 'https://${containerApp.properties.configuration.ingress.fqdn}'
output containerAppName string = containerApp.name
