"""
Created by Fabian Gnatzig
Description: Router package.
"""

from routes.beer.beer_routes import router as beer_router
from routes.beer.bring_beer_routes import router as bring_beer_router
from routes.beer.user_beer_routes import router as user_beer_router
from routes.brewery.brewery_routes import router as brewery_router
from routes.event.event_routes import router as event_router
from routes.season.season_routes import router as season_router
from routes.team.team_routes import router as team_router
from routes.user.user_routes import router as user_router
from routes.service.service_routes import router as service_router
