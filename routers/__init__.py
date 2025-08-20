"""
Created by Fabian Gnatzig

Description: Router package.
"""

from routers.beer.beer_routes import router as beer_router
from routers.beer.bring_beer_routes import router as bring_beer_router
from routers.beer.user_beer_routes import router as user_beer_router
from routers.brewery.brewery_routes import router as brewery_router
from routers.event.event_routes import router as event_router
from routers.season.season_routes import router as season_router
from routers.team.team_routes import router as team_router
from routers.user.user_routes import router as user_router
from routers.service.service_routes import router as service_router
