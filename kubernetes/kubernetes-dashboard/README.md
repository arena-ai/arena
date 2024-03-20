# Install Dashboard

```sh
helm upgrade --install kubernetes-dashboard kubernetes-dashboard \
--repo https://kubernetes.github.io/dashboard/ \
--create-namespace --namespace kubernetes-dashboard
```

Then connect with:
`https://localhost:8443`

Get the token from the kube config:
`cat ~/.kube/config`