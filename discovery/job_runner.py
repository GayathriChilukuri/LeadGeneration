import asyncio
import csv
from typing import List

# Use absolute import so this script can be executed directly (python discovery/job_runner.py)
from discovery.google_places import google_places_client


async def run_queries_to_csv(queries: List[str], out_csv: str = "results.csv", max_per_query: int = 500):
    fieldnames = ["query", "place_url", "name", "website", "phone"]
    with open(out_csv, "w", newline='', encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for q in queries:
            print(f"Searching query: {q}")
            places = await google_places_client.search_single_query(q, max_results=max_per_query)
            print(f"Found {len(places)} places for query: {q}")
            for p in places:
                details = await google_places_client.get_place_details(p.get("place_url"))
                row = {
                    "query": q,
                    "place_url": p.get("place_url"),
                    "name": p.get("name"),
                    "website": details.get("website"),
                    "phone": details.get("phone"),
                }
                writer.writerow(row)


def run(queries: List[str], out_csv: str = "results.csv", max_per_query: int = 500):
    asyncio.run(run_queries_to_csv(queries, out_csv, max_per_query))


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python job_runner.py queries.txt [out.csv]")
        raise SystemExit(1)
    qfile = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else "results.csv"
    with open(qfile, "r", encoding="utf-8") as f:
        queries = [l.strip() for l in f.readlines() if l.strip()]
    run(queries, out)
