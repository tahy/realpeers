import logging

from aiocoap import Context, Message, GET, PUT

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def catch_exception(func):
    """
    Обработка исключений
    """
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            print('Failed to fetch resource:')
            print(e)
    return wrapper


@catch_exception
async def get_state(ip_addr):
    """
    Получение стейта анкора
    """
    request = Message(code=GET, uri='coap://%s/anchor-state' % ip_addr)
    protocol = await Context.create_client_context()
    logger.debug("Get anchor state, ip: %s" % ip_addr)
    return await protocol.request(request).response


@catch_exception
async def set_state(ip_addr, state):
    """
    Установка стейта анкора
    """
    request = Message(code=PUT, payload=state, uri='coap://%s/anchor-state' % ip_addr)
    protocol = await Context.create_client_context()
    logger.debug("Set anchor state, ip: %s" % ip_addr)
    return await protocol.request(request).response


@catch_exception
async def get_config(ip_addr):
    """
    Получение текущей конфигурации анкора
    """
    request = Message(code=GET, uri='coap://%s/anchor-config' % ip_addr)
    protocol = await Context.create_client_context()
    logger.debug("Get anchor config, ip: %s" % ip_addr)
    return await protocol.request(request).response


@catch_exception
async def set_config(ip_addr, config):
    """
    Установка текущей конфигурации анкора
    """
    request = Message(code=GET, uri='coap://%s/anchor-config' % ip_addr)
    protocol = await Context.create_client_context()
    logger.debug("Set anchor config, ip: %s" % ip_addr)
    return await protocol.request(request).response


@catch_exception
async def popqueue(ip_addr):
    """
    Опрос анкора
    """
    request = Message(code=GET, uri='coap://%s/popqueue' % ip_addr)
    protocol = await Context.create_client_context()
    logger.debug("Popqueue request, ip: %s" % ip_addr)
    return await protocol.request(request).response
