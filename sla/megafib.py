# this is fibiterate3 but using the academy hosted exchange, rather than local redis

### ==== pretend this bit is in the academy standard library ==== ###

from sla.genlib import *

import logging
import asyncio
from academy.agent import Agent, action
from academy.manager import Manager
from academy.exchange import HttpExchangeFactory
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import globus_compute_sdk as gce

### ==== pretend this bit is your user code ==== ###

import asyncio
import os


if __name__ == "__main__":
    from academy.logging import init_logging
    init_logging(level='DEBUG', extra=True+1, logfile="fibiterate.log", logfile_level='DEBUG')

async def main():
  print(f"start, main process is pid {os.getpid()}")

  import sys
  endpoint = sys.argv[1]

  print(f"will use GC endpoint {endpoint}")

  async with await Manager.from_exchange_factory(factory=HttpExchangeFactory(auth_method='globus', url="https://exchange.academy-agents.org"), executors=gce.Executor(endpoint_id=endpoint)) as m:
    print(f"got manager {m!r}")
    a = FibonacciAgent()
    ah = await m.launch(a, init_logging=True, logfile="/tmp/megafib.log", loglevel=logging.DEBUG)

    iteratorh = await ah.calc_fibs(0, 1)
    print(f"got iterator handle {iteratorh}")

    await iteratorh.ping()

    iteratorh = IteratorShim(iteratorh)

    await asyncio.sleep(5)
    print(f"slept, now will iterate...")

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
    async for n in iteratorh:
      print(n)

    final_iterator_agent_logs = iteratorh.get_interesting_logs()
    final_main_agent_logs = ah.get_interesting_logs()

    print(final_iterator_agent_logs)
    print(final_main_agent_logs)

  print("end")

if __name__ == "__main__":
    asyncio.run(main())
