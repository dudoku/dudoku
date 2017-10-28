FROM python:2.7-slim-stretch


# Install Z3.
RUN apt update && apt -y install z3=4.4.1-0.3

