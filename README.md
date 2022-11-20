# telegram-bot

A simple telegram bot.

# Running locally

1. Create python virtual environemnt (optional) `python -m venv venv` and enable it `source venb/bin/activate`
2. Install requirements `pip install -r requirements.txt`
3. Install development requirements (optional) `pip install -r dev-requirements.txt`
4. Install pre-commit hooks (optional) `pre-commit install`
5. Copy the example env variables file and change it to your secrerts `cp .env.example dev.env` Take into use `source dev.env`
6. Run the app `python src/main.py` or `docker build -t telegram-bot . && docker run --rm telegram-bot`

# Deployment

Build Docker image and deploy anywhre :) The github workflow supports Azure Container Apps.

For Azure Container Apps, the requirements are
- Docker registry
- Azure subscription
- Azure Container App Environment
- Azure Container App

In short, create an container app & create an azure service principal. Then fill in the following Github secrets and you are done. Service principal can be created with

```
az ad sp create-for-rbac --name "telegramBotGithubDeploy" --role contributor \
                            --scopes /subscriptions/<subscriotion-id>/resourceGroups/<resource-group>/providers/Microsoft.App/managedEnvironments/<azure-container-apps-environment-name> /subscriptions/<subscription-id>/resourceGroups/<resource-group>/providers/Microsoft.App/containerapps/<container-app-name> \
                            --sdk-auth
```
Githup secrets
* DOCKER_REGISTRY_USERNAME
* DOCKER_REGISTRY_PASSWORD
* DOCKER_IMAGE_NAME (e.g. yourDockerHubUsername/yourBotName)
* AZURE_SP_CREDENTIALS (output of the az ad sp create-for-rbac command. Yes, the whole json)
* AZURE_CONTAINER_APP_NAME
* AZURE_RESOURCE_GROUP
