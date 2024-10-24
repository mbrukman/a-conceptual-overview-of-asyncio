
# I'm guessing the magical method that modifies Future's is the Operating System's 'select' 
# system call. My understanding is select interupts when a given file-handle is ready to be 
# used. If we can add a Future.set_result() to that select interupt, then I think we're gravy.
# Since, once the Future's state switches to Done (a side effect of set_result), the Future's
# callbacks are invoked.  

# I've found something interesting in the asyncio source code. In base_events.py, 
# a concrete (non-abstract) BaseEventLoop class is defined. The class's definition takes
# about 1500 lines (good god). This line (line 1950) of code: self._selector.select(timeout)
# is the diamond I was looking for (I think). I believe it's used to somehow notify
# after a certain delay. The EventLoop instantiated in my module here is of type:
# _UnixSelectorEventLoop which is defined in unix_events.py in asyncio and inherits
# from BaseSelectorEventLoop which inherits from BaseEventLoop.

# The BaseSelectorEventLoop has a key instance attribute: _selector. It relies on a
# seperate module entirely: selectors! Specifically, selectors.DefaultSelector(). 
# On my machine that gives me a selectors.KqueueSelector object. Each Selector class 
# in selectors.py implements a method called select. It looks like that method
# generally relies on the module select. I think selectors.py is meant to be an easier to use
# interface into the functionality of select.py.
# The KqueueSelector, which my machine defaults to, leverages select.kqueue, as opposed to
# say select.select, select.epoll or select.kevent. 