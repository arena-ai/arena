# Install Dashboard

```sh
helm upgrade --install kubernetes-dashboard kubernetes-dashboard \
--repo https://kubernetes.github.io/dashboard/ \
--create-namespace --namespace kubernetes-dashboard
```

Then connect with:
`http://localhost:8001/api/v1/namespaces/kubernetes-dashboard/services/https:kubernetes-dashboard:https/proxy/#/login`

Get the token from the kube config:
`cat ~/.kube/config`