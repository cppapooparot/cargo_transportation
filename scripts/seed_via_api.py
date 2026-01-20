import datetime as dt
import os
import random
import string

import httpx

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000/api/v1")


def rand_plate() -> str:
    letters = "".join(random.choice(string.ascii_uppercase) for _ in range(2))
    digits = "".join(random.choice(string.digits) for _ in range(4))
    return f"{letters}{digits}"


def main() -> None:
    cars_n = int(os.getenv("CARS_N", "200"))
    drivers_n = int(os.getenv("DRIVERS_N", "200"))
    trips_n = int(os.getenv("TRIPS_N", "2000"))

    brands = ["MAN", "Volvo", "Scania", "DAF", "Iveco", "Mercedes"]
    categories = ["C", "CE"]
    cargo_names = [
        "fresh apples",
        "frozen fish",
        "medical supplies",
        "car parts",
        "construction sand",
        "electronics",
        "textile",
        "glass bottles",
        "chemicals",
        "books",
    ]
    cargo_tags = [
        "fragile",
        "food",
        "cold",
        "hazmat",
        "sealed",
        "oversized",
        "documents",
        "priority",
    ]

    cars: list[str] = []
    drivers: list[str] = []

    def _fetch_existing_numbers(client: httpx.Client, path: str, key: str) -> list[str]:
        r = client.get(f"{BASE_URL}/{path}")
        if r.status_code != 200:
            return []
        data = r.json()
        if not isinstance(data, list):
            return []
        out: list[str] = []
        for item in data:
            if isinstance(item, dict) and key in item and isinstance(item[key], str):
                out.append(item[key])
        return out

    def _ensure_non_empty(name: str, items: list[str]) -> None:
        if not items:
            raise RuntimeError(f"seed failed: {name} is empty")

    with httpx.Client(timeout=30.0) as client:
        # cars
        for _ in range(cars_n):
            number = rand_plate()
            payload = {
                "number": number,
                "brand": random.choice(brands),
                "capacity_kg": random.choice([5000, 8000, 12000, 20000]),
                "fuel_l_per_100km": random.choice([18, 22, 25, 30]),
            }
            r = client.post(f"{BASE_URL}/cars", json=payload)
            if r.status_code in (200, 201):
                cars.append(number)

        if not cars:
            cars = _fetch_existing_numbers(client, "cars", "number")
        _ensure_non_empty("cars", cars)

        # drivers
        for i in range(drivers_n):
            tab_number = f"T{i:05d}"
            payload = {
                "tab_number": tab_number,
                "full_name": f"Driver {i}",
                "category": random.choice(categories),
            }
            r = client.post(f"{BASE_URL}/drivers", json=payload)
            if r.status_code in (200, 201):
                drivers.append(tab_number)

        if not drivers:
            drivers = _fetch_existing_numbers(client, "drivers", "tab_number")
        _ensure_non_empty("drivers", drivers)

        # trips
        today = dt.date.today()
        for _ in range(trips_n):
            dep = today - dt.timedelta(days=random.randint(0, 365))
            ret = dep + dt.timedelta(days=random.randint(1, 14))
            name = random.choice(cargo_names)
            tags = random.sample(cargo_tags, k=random.randint(1, 3))
            payload = {
                "departure_date": dep.isoformat(),
                "return_date": ret.isoformat(),
                "origin": random.choice(["Yerevan", "Gyumri", "Vanadzor", "Tbilisi", "Batumi"]),
                "destination": random.choice(["Yerevan", "Gyumri", "Vanadzor", "Tbilisi", "Batumi"]),
                "distance_km": random.randint(20, 1200),
                "car_number": random.choice(cars),
                "driver_tab_number": random.choice(drivers),
                "cargo": {
                    "name": name,
                    "description": f"delivery of {name}",
                    "tags": tags,
                },
            }
            client.post(f"{BASE_URL}/trips", json=payload)

    print("seed done", {"cars": len(cars), "drivers": len(drivers), "trips": trips_n})


if __name__ == "__main__":
    main()
