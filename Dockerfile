FROM python:3.9

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY . .

# Get secret openai_api_key and output it to /test at buildtime
RUN --mount=type=secret,id=openai_api_key,mode=0444,required=true \
   cat /run/secrets/openai_api_key > /test

RUN --mount=type=secret,id=consumer_key,mode=0444,required=true \
   cat /run/secrets/consumer_key > /test

RUN --mount=type=secret,id=consumer_secret_key,mode=0444,required=true \
   cat /run/secrets/consumer_secret_key > /test

RUN --mount=type=secret,id=access_token,mode=0444,required=true \
   cat /run/secrets/access_token > /test

RUN --mount=type=secret,id=access_token_secret,mode=0444,required=true \
   cat /run/secrets/access_token_secret > /test

RUN --mount=type=secret,id=bearer_token,mode=0444,required=true \
   cat /run/secrets/bearer_token > /test

RUN --mount=type=secret,id=hf_token,mode=0444,required=true \
   cat /run/secrets/hf_token > /test

# Set up a new user named "user" with user ID 1000
RUN useradd -m -u 1000 user

# Switch to the "user" user
USER user

# Set home to the user's home directory
ENV HOME=/home/user \
	PATH=/home/user/.local/bin:$PATH

# Set the working directory to the user's home directory
WORKDIR $HOME/app

# Copy the current directory contents into the container at $HOME/app setting the owner to the user
COPY --chown=user . $HOME/app

CMD ["python", "main.py"]