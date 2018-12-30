import asyncio
import asynctest
from runtime.networking import make_rpc_server
from runtime.store import StoreService
from runtime.util import AsyncThread
from runtimeclient import RuntimeClient


class TestStoreService(asynctest.TestCase):
    host, port = '127.0.0.1', 6200

    async def setUp(self):
        self.service = StoreService({
            'dev_names': 'test-dev-names.yaml',
        })
        # self.thread = AsyncThread(target=run_rpc_server,
        #                           args=(self.service, self.host, self.port))
        # self.thread.start()

    # async def test_set_alliance(self):
    #     async with RuntimeClient(self.host, self.port) as client:
    #         await client.set_alliance('blue')
    #         self.assertEqual((await client.get_field_parameters())['alliance'], 'blue')
    #
    # async def test_set_starting_zone(self):
    #     async with RuntimeClient(self.host, self.port) as client:
    #         await client.set_starting_zone('shelf')
    #         self.assertEqual((await client.get_field_parameters())['startingzone'], 'shelf')


if __name__ == '__main__':
    asynctest.main()
