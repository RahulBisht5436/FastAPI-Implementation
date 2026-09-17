import asyncio

shared_resource = "Hello i am a shared resource which is locked by a semaphore"
shared_resource_lock = asyncio.Semaphore(2)

condition = asyncio.Condition()

productArray = []

async def consumer():
    global productArray
    async with condition:
        if not productArray:
            print("No products to consume")
            await condition.wait()
    product = productArray.pop(0)
    print(f"Consumed {product}")

async def producer(product):
    global productArray
    async with condition:
        productArray.append(product)
        print(f"Produced product has been pushed to queue")
        condition.notify()


async def main():
    await asyncio.gather(
        consumer(),
        producer("Product 1"),
        consumer(),
        producer("Product 2"),
        consumer(),
        producer("Product 3"),
        consumer(),
        producer("Product 4"),
        consumer(),
        producer("Product 5")
    )

asyncio.run(main())