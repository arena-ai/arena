# Install Dashboard

```sh
helm upgrade --install kubernetes-dashboard kubernetes-dashboard \
--repo https://kubernetes.github.io/dashboard/ \
--create-namespace --namespace kubernetes-dashboard
```

Connect with: `kubectl -n kubernetes-dashboard port-forward svc/kubernetes-dashboard-kong-proxy 8443:443`

Then connect with: `https://localhost:8443`

Get the token from the kube config: `cat ~/.kube/config` or through the `aws eks get-token --cluster-name $CLUSTER_NAME --region $REGION` command.
