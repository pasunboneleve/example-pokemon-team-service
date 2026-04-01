FROM public.ecr.aws/lambda/python:3.12

COPY pokemon_service ${LAMBDA_TASK_ROOT}/pokemon_service

CMD ["pokemon_service.handler.handler"]
