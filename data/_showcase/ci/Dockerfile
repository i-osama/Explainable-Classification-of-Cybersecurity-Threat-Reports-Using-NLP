# UNTESTED template (never built). CPU image for the data-free tests.
FROM python:3.13-slim
WORKDIR /work
COPY _showcase/ /work/_showcase/
RUN pip install --no-cache-dir numpy pandas scipy scikit-learn pydantic pyyaml pyarrow
ENV TTPMAP_ROOT=/work
CMD ["python", "-X", "utf8", "_showcase/scripts/run_tests.py"]
