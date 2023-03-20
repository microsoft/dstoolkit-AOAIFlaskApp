FROM python:3.9

ADD requirements.txt ./

RUN pip install -r requirements.txt
RUN pip install gunicorn

COPY flask_app flask_app

WORKDIR /flask_app

ENV PORT 8082

EXPOSE 8082

# When running our docker image using "docker run" this command gets run
# This will start our gunicorn web server and run our app
ENTRYPOINT ["gunicorn", "--timeout", "600", "--access-logfile", "'-'", "--error-logfile", "'-'", "app:app"]
