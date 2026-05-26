
TEST_DOCKER_COMPOSE := "docker compose -f tests/test.docker-compose.yml"

test:
  {{TEST_DOCKER_COMPOSE}} up -d && docker logs -f tests

test-up:
    {{TEST_DOCKER_COMPOSE}} up -d


test-rebuild:
  {{TEST_DOCKER_COMPOSE}} up -d --build && docker logs -f tests


test-down:
  {{TEST_DOCKER_COMPOSE}} down

ruff:
    ruff check --config pyproject.toml --fix


up:
   docker compose up -d && docker exec api uv run alembic upgrade head


down:
    docker compose down