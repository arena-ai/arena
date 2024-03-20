# Arena Helm chart

Run `helm dependency update`

Install CRDs first: `kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.14.4/cert-manager.crds.yaml`
Following [cert-manager](https://cert-manager.io/docs/installation/helm/#option-1-installing-crds-with-kubectl) documentation.

Then deploy the app
```sh
helm install <release-name> arena 
```