import concurrent.futures
from typing import List, Callable, TypeVar

from exceptions.processing_exception import ProcessingError

T = TypeVar('T')
R = TypeVar('R')

def parallel_map(func: Callable[[T], R], items: List[T], max_workers: int = None) -> List[R]:
    if not items:
        return []

    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_item = {executor.submit(func, item): key for key, item in enumerate(items)}

        for future in concurrent.futures.as_completed(future_to_item):
            key = future_to_item[future]
            try:
                result = future.result()
                results.append((key, result))
            except Exception as error:
                raise error

    results.sort(key=lambda x: x[0])
    return [result[1] for result in results]
