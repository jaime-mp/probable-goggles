# * image to start from
FROM python:3.9-alpine3.13
LABEL mantainer="jaimemp"

# * tells Python that you don't want to buffer the output, so you can see the execution
ENV PYTHONUNBUFFERED 1

# * copies the requirements.txt to the /temp directory of the container
COPY ./requirements.txt /tmp/requirements.txt
COPY ./requirements.dev.txt /tmp/requirements.dev.txt
# * copy the project's app directory to the direct /app directory of the container
COPY ./app /app
# * set the working directory of the container, on which the commands will be executed
WORKDIR /app
# * expose port 8000 of the container
EXPOSE 8000

ARG DEV=false
# * run when the image is being constructed
# * create a venv in /py
RUN python -m venv /py && \
    # * update pip
    /py/bin/pip install --upgrade pip && \
    # * client package that we're going to need installed inside our Alpine image in order to be able to connect to Postgres
    apk add --update --no-cache postgresql-client jpeg-dev && \
    apk add --update --no-cache --virtual .tmp-build-deps \
        build-base postgresql-dev musl-dev zlib zlib-dev && \
    # * install the requirements in the venv
    /py/bin/pip install -r /tmp/requirements.txt && \
    if [ $DEV = true ]; \
        then /py/bin/pip install -r /tmp/requirements.dev.txt ; \
    fi && \
    # * remove the contents of the /tmp directory
    rm -rf /tmp/ && \
    apk del .tmp-build-deps && \
    # * add user django-user, without password and without home
    adduser \
        --disabled-password \
        --no-create-home \
        django-user && \
    mkdir -p /vol/web/media && \
    mkdir -p /vol/web/static && \
    chown -R django-user:django-user /vol && \
    chmod -R 755 /vol

# * create an environment variable for our venv
ENV PATH="/py/bin:$PATH"

# * specify the user to be used
USER django-user