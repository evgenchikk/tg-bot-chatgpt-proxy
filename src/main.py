import asyncio
import logging

from dotenv import load_dotenv

from config import config
from repo import Repository, get_repository
from service import Service, ServiceImpl
from controller import Controller, TGController


load_dotenv('.env')

LOG_LEVEL = logging.DEBUG if config.get('debug') else logging.INFO
LOG_FORMAT = '[%(asctime)s] [%(levelname)s] %(name)s: %(message)s'

logging.basicConfig(
    level=LOG_LEVEL,
    format=LOG_FORMAT,
)

log = logging.getLogger('main')

async def main():
    try:
        repository: Repository = get_repository(repository_key := config.get('repository', {}).get('key', 'sqlite'))
    except KeyError:
        log.error(f'Setup repository failed - no such repository key: {repository_key}. Exiting now')
        return

    try:
        service: Service = ServiceImpl(repository=repository, config=config['service'])
    except KeyError:
        log.error('Setup service failed - no config provided. Exiting now')
        return
    except Exception as e:
        log.error('Initializing OpenAIClientService failed', exc_info=e)
        return

    controller: Controller = TGController(service=service)
    log.info('Initialized. Starting...')

    try:
        await controller.run()
    except KeyboardInterrupt:
        log.log('Got interrupt, exiting')
        return


if __name__ == '__main__':
    asyncio.run(main())
