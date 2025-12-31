import os

import httpx

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000/api/v1")


def main() -> None:
    patterns = ["apple", "fish", "medical", "electronics", "glass", "hazmat"]

    with httpx.Client(timeout=30.0) as client:
        for p in patterns:
            r = client.get(
                f"{BASE_URL}/trips/search-cargo",
                params={"pattern": p, "offset": 0, "limit": 3},
            )
            r.raise_for_status()
            data = r.json()
            ids = [t.get("id") for t in data if isinstance(t, dict)]
            print(p, len(data), ids)


if __name__ == "__main__":
    main()
