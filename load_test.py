#!/usr/bin/env python3
"""Load test: Book Catalog API — read-only workload."""
import asyncio
import time
import random
import sys
from dataclasses import dataclass, field

import aiohttp

BASE_URL = "http://localhost:8000"
CONCURRENCY = 50

ENDPOINT_MIX = {
    "list_books":    6000,
    "get_book":      4500,
    "list_authors":  2250,
    "list_genres":   2250,
}

BOOK_TEMPLATE = {
    "title": "Load Test Book",
    "author": "Test Author",
    "genre": "Testing",
    "year": 2024,
    "description": "Created during load test",
}

GENRES = ["Fiction", "Non-Fiction", "Sci-Fi", "Fantasy", "Biography", "History", "Mystery", "Romance"]


@dataclass
class Stats:
    count: int = 0
    errors: int = 0
    total_time: float = 0.0
    min_time: float = float('inf')
    max_time: float = 0.0
    times: list = field(default_factory=list)

    def add(self, elapsed: float, error: bool = False):
        self.count += 1
        if error:
            self.errors += 1
        self.total_time += elapsed
        if elapsed < self.min_time:
            self.min_time = elapsed
        if elapsed > self.max_time:
            self.max_time = elapsed
        self.times.append(elapsed)

    @property
    def avg(self):
        return self.total_time / self.count if self.count else 0

    @property
    def rps(self):
        return self.count / self.total_time if self.total_time else 0

    def percentile(self, p):
        if not self.times:
            return 0
        return sorted(self.times)[int(len(self.times) * p / 100)]


async def create_books(session: aiohttp.ClientSession, count: int) -> list[str]:
    ids: list[str] = []
    for i in range(count):
        data = {
            **BOOK_TEMPLATE,
            "title": f"Load Test Book {i}_{random.randrange(1_000_000, 9_999_999)}",
            "author": f"Author {i % 30}",
            "genre": random.choice(GENRES),
        }
        async with session.post("/books", json=data) as resp:
            if resp.status == 201:
                book = await resp.json()
                ids.append(book["id"])
            else:
                print(f"  Не удалось создать тестовую книгу {i}: HTTP {resp.status}")
    return ids


def build_tasks(read_ids: list[str]) -> list[tuple[str, str, str, dict]]:
    tasks: list[tuple[str, str, str, dict]] = []

    for _ in range(ENDPOINT_MIX["list_books"]):
        params = {}
        r = random.random()
        if r < 0.3:
            params["search"] = random.choice(["Test", "Load", "Book", ""])
        elif r < 0.5:
            params["author"] = f"Author {random.randrange(0, 30)}"
        elif r < 0.6:
            params["genre"] = random.choice(GENRES)
        tasks.append(("list_books", "GET", "/books", {"params": params}))

    for _ in range(ENDPOINT_MIX["get_book"]):
        if read_ids:
            tasks.append(("get_book", "GET", f"/books/{random.choice(read_ids)}", {}))

    for _ in range(ENDPOINT_MIX["list_authors"]):
        tasks.append(("list_authors", "GET", "/authors", {}))

    for _ in range(ENDPOINT_MIX["list_genres"]):
        tasks.append(("list_genres", "GET", "/genres", {}))

    random.shuffle(tasks)
    return tasks


async def worker(
    sem: asyncio.Semaphore,
    session: aiohttp.ClientSession,
    stats: dict[str, Stats],
    task: tuple[str, str, str, dict],
):
    endpoint, method, url, kwargs = task
    async with sem:
        t0 = time.monotonic()
        try:
            async with session.request(method, url, **kwargs) as resp:
                elapsed = time.monotonic() - t0
                await resp.read()
                stats[endpoint].add(elapsed, resp.status >= 400)
        except Exception:
            elapsed = time.monotonic() - t0
            stats[endpoint].add(elapsed, error=True)


def print_stats(stats: dict[str, Stats], total_time: float):
    total_req = sum(s.count for s in stats.values())
    total_err = sum(s.errors for s in stats.values())

    print(f"\n{'='*86}")
    print(f"  Общее время: {total_time:.2f}с  |  Запросов: {total_req}  |  "
          f"Ошибок: {total_err} ({total_err/total_req*100:.1f}%)  |  "
          f"RPS: {total_req/total_time:.1f}")
    print(f"{'='*86}")
    h = f"{'Эндпоинт':<22} {'Кол-во':>6} {'Ошибки':>6} {'Мин(мс)':>8} "
    h += f"{'Ср(мс)':>8} {'Макс(мс)':>8} {'P95(мс)':>8} {'P99(мс)':>8} {'RPS':>8}"
    print(h)
    print("-" * 86)
    names = ["list_books", "get_book", "list_authors", "list_genres"]
    for name in names:
        s = stats[name]
        if s.count == 0:
            continue
        print(
            f"{name:<22} {s.count:>6} {s.errors:>6} "
            f"{s.min_time*1000:>8.1f} {s.avg*1000:>8.1f} {s.max_time*1000:>8.1f} "
            f"{s.percentile(95)*1000:>8.1f} {s.percentile(99)*1000:>8.1f} {s.rps:>8.1f}"
        )
    print("-" * 86)


async def main():
    print("=" * 86)
    print("  Нагрузочный тест: Book Catalog API")
    print(f"  Цель: {BASE_URL}  |  Параллельность: {CONCURRENCY}")
    print("=" * 86)

    async with aiohttp.ClientSession(base_url=BASE_URL) as session:
        print("\n[Подготовка] Создание тестовых книг...")
        all_ids = await create_books(session, 350)
        if len(all_ids) < 150:
            print("ОШИБКА: Не удалось создать достаточно тестовых книг. API запущен?")
            sys.exit(1)
        print(f"[Подготовка] Создано {len(all_ids)} тестовых книг")

        print("[Подготовка] Формирование очереди задач...")
        tasks = build_tasks(all_ids)
        print(f"[Подготовка] Очередь задач: {len(tasks)} запросов")

        stats = {name: Stats() for name in [
            "list_books", "get_book", "list_authors", "list_genres",
        ]}
        sem = asyncio.Semaphore(CONCURRENCY)
        coros = [worker(sem, session, stats, t) for t in tasks]

        print(f"\n[Выполнение] Отправка запросов (параллельность={CONCURRENCY})...")
        t0 = time.monotonic()
        await asyncio.gather(*coros)
        total_time = time.monotonic() - t0

        print_stats(stats, total_time)


if __name__ == "__main__":
    asyncio.run(main())
