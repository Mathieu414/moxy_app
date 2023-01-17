# Moxy app

App to help analyzing [moxy](https://www.moxymonitor.com/) data from VO2 tests and training sessions.

Using a venv or docker to develop locally, and a docker image for production

inspired by [this tuto](https://towardsdatascience.com/deploy-containerized-plotly-dash-app-to-heroku-with-ci-cd-f82ca833375c)

## Run locally with docker image

To run the image locally, cd into the moxy-app folder and:

```
docker build -t moxy-app project/.
```

And run the container

```
docker run -p 8050:8050 docker-dash
```

You can find to the app on your local machine http://localhost:8050/ (or localhost:8050). This way the image is created using the Dockerfile, instead of the Dockerfile.prod.
