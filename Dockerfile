FROM python:3.13

#Set the working directory
WORKDIR /app

COPY pyproject.toml .
COPY README.md .

#copy all the files
RUN mkdir factorio_web
COPY factorio_web factorio_web/
RUN python -m pip install .
#Expose the required port
EXPOSE 8001

#Run the command
CMD ["granian", "--interface", "asgi", "factorio_web:app", "--host", "0.0.0.0", "--port", "8001"]