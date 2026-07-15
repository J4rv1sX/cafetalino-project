from app.schemas.routing import Location

# Placeholder roster of Cafetalino vending-machine sites in Sucre, ported from
# rutas_cafetalino.ipynb. Once the predictive-stockout module and its CSV/DB
# backing exist, this should be replaced by the list of machines it flags for
# that day instead of being a fixed constant.
MACHINE_LOCATIONS: list[Location] = [
    Location(name="PIAR", lat=-19.041444, lng=-65.239213),
    Location(name="Gineco", lat=-19.045308, lng=-65.268384),
    Location(name="Seguro Social Universitario", lat=-19.048775, lng=-65.265841),
    Location(name="CREDIAUTO", lat=-19.036436, lng=-65.241630),
    Location(name="Aeropuerto Alcantari 2", lat=-19.246551, lng=-65.151120),
    Location(name="Av. Del Maestro", lat=-19.036352, lng=-65.258767),
    Location(name="Cristo de las Americas", lat=-19.045055, lng=-65.268787),
    Location(name="Pompeya", lat=-19.047379, lng=-65.258479),
]
