# Arena frontend

## Testing the frontend

First launch the stack with: `docker compose up`
or `docker compose up -d` to run it in the background

Then run the local frontend server with: `npm run dev`

## The frontend is pushed to github container registry (ghcr.io)

The frontend image is built and pushed to ghcr.io, see in `.github/workflows/publish-frontend-docker-image.yml`.
