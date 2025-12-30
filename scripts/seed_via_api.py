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

    cars: list[str] = []
    drivers: list[str] = []

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

        # trips
        today = dt.date.today()
        for _ in range(trips_n):
            dep = today - dt.timedelta(days=random.randint(0, 365))
            ret = dep + dt.timedelta(days=random.randint(1, 14))
            payload = {
                "departure_date": dep.isoformat(),
                "return_date": ret.isoformat(),
                "origin": random.choice(["Yerevan", "Gyumri", "Vanadzor", "Tbilisi", "Batumi"]),
                "destination": random.choice(["Yerevan", "Gyumri", "Vanadzor", "Tbilisi", "Batumi"]),
                "distance_km": random.randint(20, 1200),
                "car_number": random.choice(cars),
                "driver_tab_number": random.choice(drivers),
            }
            client.post(f"{BASE_URL}/trips", json=payload)

    print("seed done", {"cars": len(cars), "drivers": len(drivers), "trips": trips_n})


if __name__ == "__main__":
    main()
