# Kubernetes administration

## Troubleshoot Nginx ingress controller

Following: https://kubernetes.github.io/ingress-nginx/troubleshooting/

`kubectl get ing -n <namespace-of-ingress-resource>`

`kubectl describe ing <ingress-resource-name> -n <namespace-of-ingress-resource>`

`kubectl get pods`

## Cert Manager

As explained in https://cert-manager.io/docs/installation/helm/
We need to define CRDs

`kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.14.2/cert-manager.crds.yaml`
