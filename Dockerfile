FROM public.ecr.aws/lambda/python:3.12

COPY python/src/pokemon_service ${LAMBDA_TASK_ROOT}/pokemon_service
COPY frontend ${LAMBDA_TASK_ROOT}/frontend

CMD ["pokemon_service.handler.handler"]
