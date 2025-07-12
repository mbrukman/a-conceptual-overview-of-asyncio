import time
import selectors

# This is the Selector chosen by DefaultSelector on my machine -- Mac M1.
# I'm hard-coding it for easier snooping into its' methods.
kqueue_selector = selectors.KqueueSelector()



start_time = time.time()
with open("candy-database", "r") as fh:
    
    selector_key = kqueue_selector.register(fileobj=fh, events=selectors.EVENT_READ)
    print("A")
    v = kqueue_selector.select()
    print("B")
    import ipdb; ipdb.set_trace()
    db = fh.read()
print(f"Reading candy-database took: {time.time() - start_time:.2f} seconds.")
