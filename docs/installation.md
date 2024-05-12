---
title: Get started using Arena on Kubernetes in 10 minutes
---

# Deploying Arena on Azure AKS in three simple steps

In this post we will describe each the deployment of Arena on Azure AKS.
The deployment procedure will consist in three main steps:

1. Provisioning the k8s cluster
2. Setting up the IP, domain name and TLS certificate.
3. Deploying arena helm chart

# First step: provisioning a cluster

To provision an AKS cluster on Azure, you'll need an azure account.

You'll also need [Azure command line interface](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli) (`az`) and [Kubernetes command line tool](https://kubernetes.io/docs/reference/kubectl/) (`kubectl`)
Make sure you have them installed.

You can create a cluster [in many ways](https://learn.microsoft.com/en-us/azure/aks/learn/quick-kubernetes-deploy-cli). In this document we will focus on using the CLI.

## Create a few environment variables:
```sh
export RANDOM_ID="$(openssl rand -hex 3)"
export RESOURCE_GROUP_NAME="arena"
export REGION="westeurope"
export CLUSTER_NAME="arena"
export SUBSCRIPTION_ID="your id"
export DNS_LABEL="arena"
export NODE_RESOURCE_GROUP_NAME="arena_nodes"
```

Set them to fit your needs. Make sure the region you choose enables the provisioning of GPUs.

## Create a resource group

```sh
az group create --name $RESOURCE_GROUP_NAME --location $REGION
```

## Create the cluster

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

## Get the credentials

```sh
az aks get-credentials --resource-group $RESOURCE_GROUP_NAME --name $CLUSTER_NAME
```

