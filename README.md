# chatassist

## Architecture

Typescript Next.js frontend deployed to Vercel with serverless python functions for inference. tRPC communication between frontend and backend. Firebase auth, MongoDB state, Firebase storage file hosting.

## Development

Make sure you have docker, node v16, python 3.9 installed.

Populate your .env (in the root) with environment variables. Then run

```sh
# install build dependencies, yarn
npm i yarn
# link js dependencies
yarn
# start server
bash ./bin/dev_in_container.sh
# the following commands are run inside the docker container
# sign in to vercel, creating a new project as you won't be deploying,
# and add your environment variables from .env
bash ./bin/vercel_env.sh .env
# start the dev server
yarn dev

# in another terminal window:
cd packages/server
# follow instructions in README.md
```

The app will then be available on localhost:3000. Whenever you edit a file, it will trigger a recompilation.

Due to an issue with vercel's local development system, we have to run it in a container. It also takes a while to build the python functions. If its too much of a pain let me know.

Note: we commit the yarn cache (.yarn/cache), this is not a mistake. This is to ensure same exact dependencies on local vs in prod for more consistent builds.

