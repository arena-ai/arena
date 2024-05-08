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


