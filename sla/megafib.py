# this is fibiterate3 but using the academy hosted exchange, rather than local redis

### ==== pretend this bit is in the academy standard library ==== ###

from sla.genlib import *

import logging
import asyncio
from academy.agent import Agent, action
from academy.manager import Manager
from academy.exchange import HttpExchangeFactory, LocalExchangeFactory
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import globus_compute_sdk as gce

### ==== pretend this bit is your user code ==== ###


logger = logging.getLogger(__name__)

import asyncio
import os


if __name__ == "__main__":
    from academy.logging import recommended_dev_log_config
    lc = recommended_dev_log_config()
    lc.init_logging()

async def main(lc):
  logger.info(f"start, main process is pid {os.getpid()}")


  import sys
  if len(sys.argv) == 2:
    endpoint = sys.argv[1]

    logger.info(f"will use GC endpoint {endpoint}")
    manager = Manager.from_exchange_factory(factory=HttpExchangeFactory(auth_method='globus', url="https://exchange.academy-agents.org"), executors=gce.Executor(endpoint_id=endpoint))
  else:  # single process mode
    manager = Manager.from_exchange_factory(factory=LocalExchangeFactory(), executors=ThreadPoolExecutor())

  async with await manager as m:
    logger.info(f"got manager {m!r}")
    a = FibonacciAgent()
    ah = await m.launch(a, log_config=lc)

    iteratorh = await ah.calc_fibs(0, 1)
    logger.info(f"got iterator handle {iteratorh}")

    await iteratorh.ping()

    iterator_shim = IteratorShim(iteratorh)

    await asyncio.sleep(5)
    logger.info(f"slept, now will iterate...")

    # the error handling/logging around iteratorh not having a
    # the right async iterator __aiter__ is quite chaotic and
    # confusing: somehow badness happens when leaving the enclosing
    # `async with` block on the exception which is sometimes
    # disguising that message. that's worthy of further investigation.
    # once I did some academy source code hacking to discover that
    # error (!)... i'll make some progress on implementing __aiter__
    # I hope.

    # this fails because iteratorh Handle doesn't have an __aiter__ attribute
    # (because all the actions are generated on demand, and this doesn't
    # demand them hard enough...)
    # but maybe a Handle should be able to do that with an RPC?
    async for n in iterator_shim:
      logger.info(n)

    final_iterator_agent_logs = await iteratorh.get_interesting_logs()
    final_main_agent_logs = await ah.get_interesting_logs()

  print(final_iterator_agent_logs)
  print(final_main_agent_logs)

  logger.info("end")

if __name__ == "__main__":
    asyncio.run(main(lc))
