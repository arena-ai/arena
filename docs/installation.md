---
title: Get started using Arena on Kubernetes in 10 minutes
---

# Deploying Arena on Azure AKS in three simple steps

In this short post we will describe the deployment of Arena on Azure AKS.
The deployment procedure will consist in three main steps:

1. Provisioning the k8s cluster and connecting to it.
2. Setting up the public IP, domain name and TLS certificate.
3. Deploying `arena` using `helm`.

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

The *resource group* is where the resources created by the user for the cluster are created.

```sh
az group create --name $RESOURCE_GROUP_NAME --location $REGION
```

Another group: the *node resource group* is created with the cluster and will contain the resources automatically created for the functioning of the cluster, such as VMs etc.

## Create the cluster

The cluster can be created with the command below:

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

We can add a nodepool in `user` mode. There are two modes for nodepools: `user` and `system` modes. [Pods](https://kubernetes.io/docs/concepts/workloads/pods/) for the system are allocated in priority to nodepools in `system` mode.

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

To connect to the cluster you need to get credentials.

```sh
az aks get-credentials --resource-group $RESOURCE_GROUP_NAME --name $CLUSTER_NAME
```

Then use `kubectl` to access the cluster:

```sh
# E.g.
kubectl get nodes
```

## Check the cluster

You can check the cluster configuration this way:

```sh
az aks show --name $CLUSTER_NAME --resource-group $RESOURCE_GROUP_NAME
```

You can list the nodepools this way:

```sh
az aks nodepool list --cluster-name $CLUSTER_NAME --resource-group $RESOURCE_GROUP_NAME
```

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




# Third and last step: deployment.