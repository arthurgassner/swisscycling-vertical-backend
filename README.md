# swisscycling-vertical-backend

<p align="center">🚀 <a href="https://swisscycling-vertical.arthurgassner.ch"><strong>live website</strong></a> 🚀</p>

This repo contains the code for the backend of _The Vertical_'s website.
_The Vertical_ is a swiss cycling challenge consisting of cycling from Switzerland's northernmost point to Switzerland's southernmost point.  

The backend handles the storing/serving of records to be displayed on the frontend. 
It is built in Python, leveraging FastAPI for handling routes and Docker for containerization.

This backend is a simple FastAPI for storing/retrieving records to be displayed on the frontend.

> [!NOTE]  
> The code for the frontend can be found [here](https://github.com/arthurgassner/swisscycling-vertical-frontend).

## How to run

To run it, run `docker compose up --build`.