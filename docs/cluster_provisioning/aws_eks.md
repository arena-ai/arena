---
title: Provisioning an AWS-EKS cluster
---

# Deploying [Arena](https://github.com/arena-ai/arena) on AWS EKS

To provision an [EKS cluster on AWS](https://docs.aws.amazon.com/eks/latest/userguide/create-cluster.html), you'll need an AWS account.

You'll also need [EKS command line interface](https://eksctl.io/) (`eksctl`) and [Kubernetes command line tool](https://kubernetes.io/docs/reference/kubectl/) (`kubectl`).
Make sure you have them installed.

## Create a few environment variables

You can parametrize the deployment of [Arena](https://github.com/arena-ai/arena) using environment variables:
```sh
export CLUSTER_NAME="arena-staging"
export REGION="eu-north-1"
export NODE_GROUP_NAME="arena-nodes"
```

Set them to fit your needs. Make sure the region you choose enables the provisioning of GPUs if you plan to use AI model fine-tuning features.

## Create the cluster

The cluster itself can be created with the command below:

```sh
eksctl create cluster --name $CLUSTER_NAME --region $REGION --version 1.30 --without-nodegroup
```

We then add nodes to our cluster by creating nodegroups

```sh
eksctl create nodegroup \
  --cluster $CLUSTER_NAME \
  --region $REGION \
  --name $NODE_GROUP_NAME \
  --node-ami-family Ubuntu2204 \
  --node-type m5.xlarge \
  --nodes 3 \
  --nodes-min 2 \
  --nodes-max 5
```

## Check you can access the cluster

```sh
# E.g.
kubectl get nodes
```

## Create an IAM OIDC provider

See [documentation](https://docs.aws.amazon.com/eks/latest/userguide/enable-iam-roles-for-service-accounts.html)

```sh
OIDC_ID=$(aws eks describe-cluster --name $CLUSTER_NAME  --region $REGION --query "cluster.identity.oidc.issuer" --output text | cut -d '/' -f 5)
aws iam list-open-id-connect-providers | grep $OIDC_ID | cut -d "/" -f4
eksctl utils associate-iam-oidc-provider --cluster $CLUSTER_NAME --approve --region $REGION
```

## Install EBS CSI driver

See [documentation](https://docs.aws.amazon.com/eks/latest/userguide/ebs-csi.html)

To provision storage, Kubernetes uses [CSI](https://kubernetes.io/docs/concepts/storage/volumes/#csi)

[Associate service account role](https://docs.aws.amazon.com/eks/latest/userguide/associate-service-account-role.html)

Create Amazon EBS CSI driver IAM role:
```sh
export IAM_ROLE_NAME=$(echo "$CLUSTER_NAME" | awk -F '-' '{for(i=1; i<=NF; i++) $i=toupper(substr($i,1,1)) substr($i,2)} 1' OFS="")EBSCSIDriverRole
eksctl create iamserviceaccount \
  --name ebs-csi-controller-sa \
  --namespace kube-system \
  --cluster $CLUSTER_NAME \
  --role-name $IAM_ROLE_NAME \
  --role-only \
  --attach-policy-arn arn:aws:iam::aws:policy/service-role/AmazonEBSCSIDriverPolicy \
  --approve
```

### Confirm that the role and service account are configured correctly.

Confirm that the IAM role's trust policy is configured correctly.

```sh
aws iam get-role --role-name $IAM_ROLE_NAME --query Role.AssumeRolePolicyDocument
```

Confirm that the policy that you attached to your role in a previous step is attached to the role.

```sh
aws iam list-attached-role-policies --role-name $IAM_ROLE_NAME --query "AttachedPolicies[0].PolicyArn" --output text
```

### Add the EBS CSI add-on

```sh
eksctl create addon --name aws-ebs-csi-driver \
  --cluster $CLUSTER_NAME \
  --region $REGION \
  --service-account-role-arn arn:aws:iam::$(aws sts get-caller-identity --query Account --output text):role/${IAM_ROLE_NAME} --force
```

You can verify that the EBS CSI driver has been installed by checking the add-ons in your cluster:

```sh
aws eks describe-addon --cluster-name $CLUSTER_NAME --addon-name aws-ebs-csi-driver
```

## Check the cluster configuration

You have now a working cluster ready to run the [Arena](https://github.com/arena-ai/arena) app

## Connect to Kubernetes Dashboard

Run:

```sh
kubectl -n kubernetes-dashboard port-forward svc/kubernetes-dashboard-kong-proxy 8443:443
```

Then connect to [the web interface](https://localhost:8443/).

Use this command to get the token required to login:

```sh
aws eks get-token --cluster-name $CLUSTER_NAME --region $REGION
```
