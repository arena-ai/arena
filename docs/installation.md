---
title: Get started using Arena on Kubernetes in 10 minutes
---

# Deploying [Arena](https://github.com/arena-ai/arena) on Azure AKS in three simple steps

In this short post we will describe the deployment of Arena on Azure AKS.
The deployment procedure will consist in three main steps:

1. Provisioning the *kubernetes* (k8s) cluster and connecting to it.
2. Setting up the public IP, domain name and TLS certificate.
3. Deploying [Arena](https://github.com/arena-ai/arena) using `helm`.

# First step: provisioning a cluster

To provision an [AKS cluster on Azure](https://azure.microsoft.com/fr-fr/products/kubernetes-service), you'll need an Azure account. Note that the installation process is relatively similar with other managed k8s such as [GKE](https://cloud.google.com/kubernetes-engine), [EKS](https://aws.amazon.com/eks/) and [the like](https://us.ovhcloud.com/public-cloud/kubernetes/).

You'll also need [Azure command line interface](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli) (`az`) and [Kubernetes command line tool](https://kubernetes.io/docs/reference/kubectl/) (`kubectl`).
Make sure you have them installed.

You can create a cluster [in many ways](https://learn.microsoft.com/en-us/azure/aks/learn/quick-kubernetes-deploy-cli). In this document we will focus on using the CLI.

## Create a few environment variables

You can parametrize the deployment of [Arena](https://github.com/arena-ai/arena) using environment variables:
```sh
export CLUSTER_NAME="arena"
export REGION="westeurope"
export SUBSCRIPTION_ID="<your_id>"
export RESOURCE_GROUP_NAME="arena"
export NODE_RESOURCE_GROUP_NAME="arena_nodes"
export DOCKER_PASSWORD="<the_token_to_access_the_docker_registry_where_images_are>"
export POSTGRES_USER="postgres"
export POSTGRES_PASSWORD="$(openssl rand -base64 12)"
export REDIS_PASSWORD="$(openssl rand -base64 12)"
export FIRST_SUPERUSER="admin@sarus.tech"
export FIRST_SUPERUSER_PASSWORD="$(openssl rand -base64 12)"
export USERS_OPEN_REGISTRATION=False
```

Set them to fit your needs. Make sure the region you choose enables the provisioning of GPUs if you plan to use AI model fine-tuning features.

## Create a resource group

The *resource group* is where the resources created by the user for the cluster are created.

```sh
az group create --name $RESOURCE_GROUP_NAME --location $REGION
```

Another group: the *node resource group* is created with the cluster and will contain the resources automatically created for the functioning of the cluster, such as VMs etc.

## Create the cluster

The cluster itself can be created with the command below:

```sh
az aks create \
    --resource-group $RESOURCE_GROUP_NAME \
    --name $CLUSTER_NAME \
    --node-count 2 \
    --subscription $SUBSCRIPTION_ID \
    --location $REGION \
    --tier standard \
    --kubernetes-version 1.28.5 \
    --auto-upgrade-channel patch \
    --node-os-upgrade-channel NodeImage \
    --nodepool-name agentpool \
    --node-vm-size Standard_D8ds_v5 \
    --enable-cluster-autoscaler \
    --min-count 2 \
    --max-count 5 \
    --node-resource-group $NODE_RESOURCE_GROUP_NAME
```

We will add a nodepool in `user` mode. There are two modes for nodepools: `user` and `system` modes. [Pods](https://kubernetes.io/docs/concepts/workloads/pods/) for the system are allocated in priority to nodepools in `system` mode so this `user` pool is mostly for the application pods.

```sh
az aks nodepool add \
--resource-group $RESOURCE_GROUP_NAME \
--name userpool \
--cluster-name $CLUSTER_NAME \
--mode user \
--node-count 2 \
--node-vm-size Standard_D8ds_v5 \
--enable-cluster-autoscaler \
--min-count 2 \
--max-count 5
```

## Get the credentials

To connect to the cluster you need credentials on your local machine. Run the following command:

```sh
az aks get-credentials --resource-group $RESOURCE_GROUP_NAME --name $CLUSTER_NAME
```
It will configure your local `kubectl` command, typically by adding entries in your `~/.kube/config` file.

Then use `kubectl` to access the cluster:

```sh
# E.g.
kubectl get nodes
```

## Check the cluster configuration

You can check the cluster configuration this way:

```sh
az aks show --name $CLUSTER_NAME --resource-group $RESOURCE_GROUP_NAME
```

You can list the nodepools this way:

```sh
az aks nodepool list --cluster-name $CLUSTER_NAME --resource-group $RESOURCE_GROUP_NAME
```

You have now a working cluster ready to run the [Arena](https://github.com/arena-ai/arena) app.

# Second step: setting up the public IP, domain name and TLS certificate

## Create a public IP

```sh
az network public-ip create --name "${CLUSTER_NAME}-ip" \
    --resource-group $NODE_RESOURCE_GROUP_NAME \
    --allocation-method Static \
    --location $REGION
```

## Set a DNS entry for your domain

In our case, we set the `A` record of `arena.sarus.app` to our newly created IP address.

## Setup autocert

Clone the [Arena](https://github.com/arena-ai/arena) repository on your local machine.

```sh
git clone https://github.com/arena-ai/arena.git
```

Change to the repository directory:

```sh
cd arena
```

### Create K8s *Custom Resources Definitions* (CRDs)

[Arena](https://github.com/arena-ai/arena) uses [*cert-manager*](https://cert-manager.io/docs/installation/helm/) to automatically get a [*letsencrypt*](https://letsencrypt.org/) TLS certificate to enable *secure https access*.
The use of *cert-manager* requires [CRDs](https://kubernetes.io/docs/tasks/extend-kubernetes/custom-resources/custom-resource-definitions/).

```sh
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.14.4/cert-manager.crds.yaml
```

### Deploy the app

The [Arena](https://github.com/arena-ai/arena) app can then be deployed:

```sh
helm upgrade --install ${RELEASE_NAME} kubernetes/arena \
	--set docker.password=${DOCKER_PASSWORD} \
	--set postgresql.user=${POSTGRES_USER} \
	--set postgresql.password=${POSTGRES_PASSWORD} \
	--set redis.password=${REDIS_PASSWORD} \
	--set backend.firstSuperUser.user=${FIRST_SUPERUSER} \
	--set backend.firstSuperUser.password=${FIRST_SUPERUSER_PASSWORD} \
	--set backend.usersOpenRegistration=${USERS_OPEN_REGISTRATION}
```

### Deploy the kubernetes dashboard

```sh
helm upgrade --install kubernetes-dashboard kubernetes-dashboard \
    --repo https://kubernetes.github.io/dashboard/ \
    --create-namespace --namespace kubernetes-dashboard
```

You can then log into the dashboard using:

```sh
kubectl --namespace kubernetes-dashboard port-forward svc/kubernetes-dashboard-kong-proxy 8443:443
```

# Third and last step: deployment.