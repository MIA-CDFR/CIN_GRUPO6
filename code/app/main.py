import uvicorn

from fastapi import FastAPI

from app.utils.geo import get_geocode_by_address

app = FastAPI()


@app.get("/geocode")
async def get_geocode(
    address: str,
    city: str | None = None,
    country: str | None = None,
):
    if city:
        geo_code = get_geocode_by_address(address=address, city=f"{city}, {country}")
    else:    
        geo_code = get_geocode_by_address(address=address)

    return {
        "lat": geo_code.y,
        "lon": geo_code.x
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
