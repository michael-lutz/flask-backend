# server

Flask server with our conversation endpoints, hosted on railways.

## local development

Ensure that you have `pyenv` set up so that we can all use the same python version. Then run

```sh
pyenv install 3.9.<whatever>
python --version
# make sure its 3.9

python -m venv venv
# Make sure to add MONGODB_URL and OPENAI_API_KEY to the environment
# by accessing your venv/bin/activate file via nano and adding the export __=___ lines to the end of the file.
source venv/bin/activate
pip install -r requirements.txt

yarn dev
```

## redirects

Requests are redirected to this server by vercel while undergoing local development. See `vercel.dev.json` for all redirected routes. More info can be found [here](https://vercel.com/docs/project-configuration#project-configuration/redirects)

## installing deps

The script `./bin/pip_install_and_save.sh` installs a dependency and saves it to requirements.txt, please do this so that prod knows what to install. For brevity run

```sh
yarn pip-install <...stuff>
```

## testing and debugging

You can run this to test backend functions when it's running

Example:
```sh
curl -d '{"question":"hello can you help?","domain":"Article"}' -H 'Content-Type: application/json' http://127.0.0.1:5000/initialize_convo_python
```
Returns: 
{"message": " Hi there! I'm a customer service chatbot for Playground. How can I help you today?", "id": "63b61a0f61724f40bf230164"}

```sh
curl -d '{"question":"hello can you help me sign in?","conversation_id":"63b61a0f61724f40bf230164"}' -H 'Content-Type: application/json' http://127.0.0.1:5000/generate_response_python
```

Returns:
{"message": " Absolutely! To sign in to the Playground app, download either the iPhone or Android app and enter your login credentials. If you get an error, double check that the email is correctly formatted and that the password is correct. If you forgot your password, check our guide on resetting it.", "id": "63b61a0f61724f40bf230164"}