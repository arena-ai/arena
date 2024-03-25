# Arena Helm chart

Run `helm dependency update`

Install CRDs first: `kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.14.4/cert-manager.crds.yaml`
Following [cert-manager](https://cert-manager.io/docs/installation/helm/#option-1-installing-crds-with-kubectl) documentation.

Then deploy the app:

```sh
helm install ${RELEASE_NAME} kubernetes/arena \
--set docker.password=${DOCKER_PASSWORD} \
--set postgresql.user=${POSTGRES_USER} \
--set postgresql.password=${POSTGRES_PASSWORD} \
--set redis.password=${REDIS_PASSWORD} \
--set backend.firstSuperUser.user=${FIRST_SUPERUSER} \
--set backend.firstSuperUser.password=${FIRST_SUPERUSER_PASSWORD}
```

Or if you use a `.env` file:

```sh
source .env; helm upgrade --install ${RELEASE_NAME} kubernetes/arena \
--set docker.password=${DOCKER_PASSWORD} \
--set postgresql.user=${POSTGRES_USER} \
--set postgresql.password=${POSTGRES_PASSWORD} \
--set redis.password=${REDIS_PASSWORD} \
--set backend.firstSuperUser.user=${FIRST_SUPERUSER} \
--set backend.firstSuperUser.password=${FIRST_SUPERUSER_PASSWORD}
```

To uninstall:

```sh
helm uninstall ${RELEASE_NAME}
```

Or:

```sh
source .env; helm uninstall ${RELEASE_NAME}
```