FROM python:3.12-slim
WORKDIR /app
ARG DATASET_VERSION=1.0.0
ENV DATASET_VERSION=${DATASET_VERSION}
LABEL dataset.version="${DATASET_VERSION}" \
      dataset.schema.version="1.0" \
      dataset.source="synthetic-practice-dataset"
COPY validate.py ./validate.py
COPY data/dataset.csv ./data/dataset.csv
RUN python validate.py
USER 10001:10001
CMD ["python", "validate.py"]
