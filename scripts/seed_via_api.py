import os
import random
import string
import datetime as dt

import httpx

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000/api/v1")

CARS_N = int(os.getenv("CARS_N", "50"))
DRIVERS_N = int(os.getenv("DRIVERS_N", "50"))
TRIPS_N = int(os.getenv("TRIPS_N", "200"))


def rand_plate() -> str:
    letters = "".join(random.choices(string.ascii_uppercase, k=2))
    digits = "".join(random.choices(string.digits, k=4))
    return f"{letters}{digits}"


def _fetch_existing_numbers(client: httpx.Client, endpoint: str, field: str) -> list[str]:
    r = client.get(f"{BASE_URL}/{endpoint}", params={"offset": 0, "limit": 1000})
    r.raise_for_status()
    items = r.json()
    out: list[str] = []
    for it in items:
        if isinstance(it, dict) and field in it:
            out.append(str(it[field]))
    return out


def main() -> None:
    cargo_names = [
        "fresh apples",
        "fish",
        "medical supplies",
        "electronics",
        "glass",
        "hazmat",
        "wood",
        "furniture",
    ]
    cities = ["Yerevan", "Gyumri", "Vanadzor", "Hrazdan", "Armavir", "Artashat"]

    with httpx.Client(timeout=30.0) as client:
        # Cars
        cars: list[str] = []
        for _ in range(CARS_N):
            payload = {
                "number": rand_plate(),
                "brand": random.choice(["MAN", "Volvo", "Scania", "DAF", "Iveco"]),
                "capacity_kg": random.randint(1000, 25000),
                "fuel_l_per_100km": random.randint(8, 40),
            }
            r = client.post(f"{BASE_URL}/cars", json=payload)
            if r.status_code in (200, 201):
                cars.append(payload["number"])

        if not cars:
            cars = _fetch_existing_numbers(client, "cars", "number")
        if not cars:
            raise RuntimeError("No cars available (create cars first)")

        # Drivers
        drivers: list[str] = []
        for i in range(DRIVERS_N):
            tab = f"T{i:05d}"
            payload = {
                "tab_number": tab,
                "full_name": f"Driver {i}",
                "category": random.choice(["B", "C", "CE"]),
            }
            r = client.post(f"{BASE_URL}/drivers", json=payload)
            if r.status_code in (200, 201):
                drivers.append(tab)

        if not drivers:
            drivers = _fetch_existing_numbers(client, "drivers", "tab_number")
        if not drivers:
            raise RuntimeError("No drivers available (create drivers first)")

        # Trips
        today = dt.date.today()
        for _ in range(TRIPS_N):
            dep = today - dt.timedelta(days=random.randint(0, 365))
            ret = dep + dt.timedelta(days=random.randint(0, 7))
            origin = random.choice(cities)
            destination = random.choice([c for c in cities if c != origin])

            payload = {
                "departure_date": dep.isoformat(),
                "return_date": ret.isoformat(),
                "origin": origin,
                "destination": destination,
                "distance_km": random.randint(20, 1200),
                "car_number": random.choice(cars),
                "driver_tab_number": random.choice(drivers),
                "cargo": {
                    "name": random.choice(cargo_names),
                    "tags": random.sample(
                        ["fragile", "food", "medical", "priority", "hazmat"],
                        k=random.randint(0, 3),
                    ),
                },
            }
            r = client.post(f"{BASE_URL}/trips", json=payload)
            r.raise_for_status()

    print("seed done", {"cars": len(cars), "drivers": len(drivers), "trips": TRIPS_N})


if __name__ == "__main__":
    main()