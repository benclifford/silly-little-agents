# this is fibiterate3 but using the academy hosted exchange, rather than local redis

### ==== pretend this bit is in the academy standard library ==== ###


import asyncio
from academy.agent import Agent, action
from academy.manager import Manager
from academy.exchange import HttpExchangeFactory
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import globus_compute_sdk as gce

from sla.logagent import LogAgent

async def async_generator_to_agent(g, m):
  """Turn a generator into an agent, so that we can then pass
     its handle around as a return result, and do RPCs for iteration.
  """
  print(f"On pid {os.getpid()}, converting generator to agent")
  # m = await Manager.from_exchange_factory(factory=HttpExchangeFactory(auth_method='globus', url="https://exchange.academy-agents.org"), executors=gce.Executor(endpoint_id='d23b9bc6-99d1-40c4-8c35-9effd8a2266c'))
  # this is explicitly not a with-block ^^^ because I want to launch a new
  # ambient agent and return the result without shutting down the infra.
  # also note that this *must* be ThreadPoolExecutor or something similar:
  # we want to be living
  # in the same process that the call was made in, without moving objects
  # around -- that's *why* we're making this agent, to avoid moving objects
  # around and instead to make the generator remotely interactable.
  # or the agent could be started locally some other way that I don't have
  # in my head, assuming that there's already an agent environment here to
  # run the FibonacciAgent...

  ag = GeneratorAgent(g)
  agh = await m.launch(ag)
  # this m manager is now leaking across the
  # boundary of what I imagined to be academy vs user land.
  print(f"GeneratorAgent launched, about to return handle {agh}")
  return agh

class GeneratorAgent(LogAgent):
  def __init__(self, g):
    print(f"initialising generator agent {self!r} on {os.getpid()}")
    self.g = g

  @action
  async def __anext__(self):
    print(f"in agent-side anext on pid {os.getpid()}")
    # i think this stuff is hanging because the agent process from
    # the above manager never terminates. I'm not sure what the right
    # pattern for that should be.
    return await self.g.__anext__()


# this is to make a Handle look right for `async for`, which wants
# __aiter__ a non-async, and __anext__ an async that is explicitly
# defined, not implicit like all Handle actions.
# use this on the client side.

class IteratorShim:
    def __init__(self, handle):
        self.handle = handle

    def __aiter__(self):
        return self

    async def __anext__(self):
        return await self.handle.__anext__()

### ==== pretend this bit is your user code ==== ###

import asyncio
import os


class FibonacciAgent(LogAgent):


  async def agent_on_startup(self):

    import asyncio
    from academy.agent import Agent, action
    from academy.manager import Manager
    from academy.exchange import HttpExchangeFactory
    from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
    import globus_compute_sdk as gce
    self.manager = Manager(
      self.agent_exchange_client,
      ThreadPoolExecutor()
    )

  async def agent_on_shutdown(self):
    await self.manager.close(close_exchange=False)
    return await super().agent_on_shutdown()

  @action
  async def calc_fibs(self, init_a, init_b):
     return await async_generator_to_agent(fibs_generator(init_a, init_b), self.manager)

async def fibs_generator(init_a, init_b):
  a = init_a
  b = init_b
  while b < 1000:
    yield f"b={b} computed on pid {os.getpid()}"
    t = a+b
    a = b
    b = t
    await asyncio.sleep(0.5)
 
