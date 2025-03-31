# Vesting Schedule

## Requirements
* python 3.13
* pipenv
* A strong will :)


## Setup

1. Setup & activate the project's virtual env
```shell
pipenv install
```

```shell
pipenv shell
```

2. Run the program
```shell
pipenv run vesting_schedule [csv_file] [target_date] [precision]
```

3. Run the tests
```shell
pytest . 
```

3. Enjoy the sunrise :')


## Final Thoughts

Spent a considerable amount of time on this - 5.5hours already over the course of two days.

I opted for a DDD approach architecture wise due to clear separation of concerns between the distinct layers:

**Models** - Domain entities
**Services** - Business Domain
**Processors** - Event Domain
**Utilities**  - Shared Domain
**Exception handling** - Exceptions Domain

Each domain & it's parts is only responsible for its domain it is in. Not only keeping it free from side effects but also ensuring the parts do one thing only & well(I hope xD)
This not only helps with maintenance but also future extensibility.
With this in mind, I ensured strong type safety throughout the project to ensure that contracts are enforced but also makes my life easier when it comes DX & support through the IDE.
This also ensure that writing tests & debugging issues was a lot easier as opposed to hours spent trying to locate what went wrong.

I also utilised concurrency management, caching & tests as well as various different design implementation patterns to suit the functionality.

### What I would improve:
* Add some more test cases around the service, I feel there are some edge cases that I've not tackled:
  * I would probably test the parallel  & sequential processing in all fairness ensuring things are truly thread safe and that threads don't overlap or bleed into eachhother during execution. 
  * Also testing how it performs with processing large amounts of data - typically this is the case when companies are giving employees RSUs, they are large corporate structures with different vesting periods, rules and thousands of employees.
  * Tests around the caching to ensure that no duplicate events are being processed but also that cache is properly invalidated ensuring that we start fresh eachtime the program is run.
  * All of this would prevent major issues and also help keep me sane.
  * I would also properly add some kind of memory tracking via a stats output of sorts to monitor the program during run but also alert us to any catastrophes such as memory leaks.

### Considerations:
The implementation of the program provides heaps of benefits outside of this specific program:
* Components Library - standalone modules such as `csv_parser.py` or any of the utils can be extracted into this.
* A Performance Benchmarking Framework -  besides missing a metric module, this can easily be built out and provide the ability to compare performance of different implementations but also identify areas of regression.

### Trade-offs With Current Implementation

#### Memory vs. Speed
While I did implement configurable processing of chunks there are issue's here:
* Smaller - can lead to more I/O ops & higher thread overhead
* Larger - Higher memory consumption but generally better throughput
- This can be solved depending on the scalability of the system architecture and how much memory is provided to each worker. Metric tracking is looking quite attractive right now xD.

#### Caching
I made a conscious decision to implement Domain model level caching instead of say using an out of the box solution like Redis. While it offers better encapsulation like always there are trade-offs to this.
* It would not be scalable to a large number of users or across multiple systems.
* Service level caching would be so much more efficient but suffer from less encapsulation.
- Redis would be the best course of action since it allows for full scalability, robustness & efficiency across multiple services but comes with additional complexity in-terms of setup. I'd likely have to dockerize the program or include a redis container in the project. So, given the nature of this program & task I went for simplicity.

#### Thread Safe
This is something I learned the hard way years ago around concurrency, memory leaks and corrupted processes when threads are processing data in parallel. Never again. This again comes with it's own cons, namely deadlocks :')
* Lock based concurrency is quite simple to implement and simple to follow if one hasn't had exposure to it before
* actor model in all honesty is just something I've not come across in the wild nor been exposed to it either.
- Kept it simple
