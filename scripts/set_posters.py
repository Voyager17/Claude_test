"""
Проставляет постеры для фильмов по названию через PATCH /api/v1/movies/{id}.
Запуск: uv run python scripts/set_posters.py
"""

import httpx

API = "http://localhost:8001/api/v1"

# Известные постеры с TMDB (https://image.tmdb.org/t/p/w500/<path>)
POSTERS: dict[str, str] = {
    "The Godfather":           "https://image.tmdb.org/t/p/w500/3bhkrj58Vtu7enYsLlegkKXKkUw.jpg",
    "The Shawshank Redemption":"https://image.tmdb.org/t/p/w500/q6y0Go1tsGEsmtFryDOJo3dEmqu.jpg",
    "Pulp Fiction":            "https://image.tmdb.org/t/p/w500/d5iIlFn5s0ImszYzBPb8JPIfbXD.jpg",
    "Schindler's List":        "https://image.tmdb.org/t/p/w500/sF1U4EUQS8YHUYjNl3pMGNIQyr0.jpg",
    "The Dark Knight":         "https://image.tmdb.org/t/p/w500/qJ2tW6WMUDux911r6m7haRef0WH.jpg",
    "Forrest Gump":            "https://image.tmdb.org/t/p/w500/saHP97rTPS5eLmrLQEcANmKrsFl.jpg",
    "Inception":               "https://image.tmdb.org/t/p/w500/9gk7adHYeDvHkCSEqAvQNLV5Uge.jpg",
    "The Matrix":              "https://image.tmdb.org/t/p/w500/f89U3ADr1oiB1s9GkdPOEpXUk5H.jpg",
    "Goodfellas":              "https://image.tmdb.org/t/p/w500/aKuFiU82s5ISJpGZp7YkIr3kCUd.jpg",
    "Se7en":                   "https://image.tmdb.org/t/p/w500/6yoghtyTpznpBik8EngEmJskVUO.jpg",
    "Fight Club":              "https://image.tmdb.org/t/p/w500/pB8BM7pdSp6B6Ih7QZ4DrQ3PmJK.jpg",
    "The Silence of the Lambs":"https://image.tmdb.org/t/p/w500/uS9m8OBk1A8eM9I042bx8XXpqAq.jpg",
    "Interstellar":            "https://image.tmdb.org/t/p/w500/gEU2QniE6E77NI6lCU6MxlNBvIx.jpg",
    "The Lord of the Rings: The Fellowship of the Ring":
                               "https://image.tmdb.org/t/p/w500/6oom5QYQ2yQTMJIbnvbkBL9cHo6.jpg",
    "Gladiator":               "https://image.tmdb.org/t/p/w500/ty8TGRuvJLPUmAR1H1nRIsgwvim.jpg",
    "The Lion King":           "https://image.tmdb.org/t/p/w500/sKCr78MXSLixwmZ8DyJLrpMsd15.jpg",
    "Titanic":                 "https://image.tmdb.org/t/p/w500/9xjZS2rlVxm8SFx8kPC3aIGCOYQ.jpg",
    "Schindler List":          "https://image.tmdb.org/t/p/w500/sF1U4EUQS8YHUYjNl3pMGNIQyr0.jpg",
}


def main() -> None:
    with httpx.Client(base_url=API, timeout=10) as client:
        movies = client.get("/movies/").json()
        print(f"Найдено фильмов: {len(movies)}")

        updated = 0
        skipped = 0
        for movie in movies:
            title = movie["title"]
            poster_url = POSTERS.get(title)
            if not poster_url:
                print(f"  [пропуск] {title!r} — постер не найден")
                skipped += 1
                continue

            resp = client.patch(f"/movies/{movie['id']}", json={"image_url": poster_url})
            if resp.status_code == 200:
                print(f"  [✓] {title}")
                updated += 1
            else:
                print(f"  [!] {title} — ошибка {resp.status_code}: {resp.text}")

    print(f"\nОбновлено: {updated}, пропущено: {skipped}")


if __name__ == "__main__":
    main()
