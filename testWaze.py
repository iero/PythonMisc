import putils.waze as waze

from_lat = 48.19601
from_long = -3.8988
to_lat = 48.18678
to_long = -3.81271

route = waze.WazeRouteCalculator(from_lat, from_long, to_lat, to_long)
route_time, route_distance = route.calc_route_info()
print(route_distance)
