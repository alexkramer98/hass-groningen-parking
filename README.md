# Parking in Groningen
## Introduction
If you have a "Bezoekersvergunning" you would like to use in Home Assistant, you can use this component.

It uses the API that this frontend interacts with: https://aanvraagparkeren.groningen.nl/DVSPortal

It exposes 4 actions:
- `groningen_parking.get_balance`: returns the balance left in minutes
- `groningen_parking.park`: starts a parking action
- `groningen_parking.unpark`: stops a parking action
- `groningen_parking.has_reservation`: returns True/False, depending on if you have an active reservation

You can use this in automations, like sending a notification when you enter the zone the Bezoekersvergunning is registered to, or sending a notification when you exited the zone but are still parked.

## How to use
1. Copy all files in here to `custom_components/groningen-parking`.
2. Restart HASS
3. Add a new integration in `Settings -> Devices and Services`.
4. Search for Groningen Parking
5. Fill out the username, password (The credentials you use to login to the portal), and license plate

## Notes
I did not create sensors for balance and reservations, as I did not want to poll the API every x minutes. Use the services to get the current state instead.

This is something I threw together. The error will not be up to standard and the API may change anytime, so this component could stop working.
