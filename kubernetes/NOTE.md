# Kubernetes administration

## Troubleshoot Nginx ingress controller

Following: https://kubernetes.github.io/ingress-nginx/troubleshooting/

`kubectl get ing -n <namespace-of-ingress-resource>`

`kubectl describe ing <ingress-resource-name> -n <namespace-of-ingress-resource>`

`kubectl get pods`

## Inspect K8s objects

`kubectl -n kubernetes-dashboard port-forward svc/kubernetes-dashboard-kong-proxy 8443:443`

To login you need the token from your `~/.kube/config` file or `aws eks get-token --cluster-name $CLUSTER_NAME --region $REGION` command.

## Inspect the Database

`kubectl port-forward statefulsets/sarus-postgresql 5432:5432`

## Cert Manager

As explained in https://cert-manager.io/docs/installation/helm/
We need to define CRDs

`kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.14.2/cert-manager.crds.yaml`
