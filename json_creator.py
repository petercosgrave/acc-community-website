import json

def create_configuration_json_file(udp_port, tcp_port, max_connections, register_to_lobby, lan_discovery):
    register_to_lobby = int(register_to_lobby == True)
    lan_discovery = int(lan_discovery == True)
    json_data = {
        "configVersion": 1,
        "udpPort": udp_port,
        "tcpPort": tcp_port,
        "maxConnections": max_connections,
        "registerToLobby": register_to_lobby,
        "lanDiscovery": lan_discovery
    }
    with open('Assetto Corsa Competizione Dedicated Server/server/cfg/configuration.json', 'w') as outfile:
        json.dump(json_data, outfile, indent=4)

def create_settings_json_file(server_name, password, admin_password, spectator_password, track_medal_requirement, 
                                            safety_rating_requirement, racecract_rating_requirement,
                                            dump_leaderboards, is_race_locked, randomize_track_when_empty,
                                            max_car_slots, central_entry_list_path, short_formation_lap,
                                            allow_auto_dq, dump_entry_list, formation_lap_type,
                                            car_group):
    dump_leaderboards = int(dump_leaderboards == True)
    is_race_locked = int(is_race_locked == True)
    randomize_track_when_empty = int(randomize_track_when_empty == True)
    short_formation_lap = int(short_formation_lap == True)
    allow_auto_dq = int(allow_auto_dq == True)
    dump_entry_list = int(dump_entry_list == True)
    json_data = {
        "configVersion": 1,
        "serverName": server_name,
        "password": password,
        "adminPassword": admin_password,
        "spectatorPassword": spectator_password,
        "trackMedalsRequirement": track_medal_requirement,
        "safetRatingRequirement": safety_rating_requirement,
        "raceCraftRatingRequirement": racecract_rating_requirement,
        "dumpLeaderboards": dump_leaderboards,
        "isRaceLocked": is_race_locked,
        "randomizeTrackWhenEmpty": randomize_track_when_empty,
        "maxCarSlots": max_car_slots,
        "centralEntryListPath": central_entry_list_path,
        "shortFormationLap": short_formation_lap,
        "allowAutoDQ": allow_auto_dq,
        "dumpEntryList": dump_entry_list,
        "formationLapType": formation_lap_type,
        "carGroup": car_group
    }
    with open('Assetto Corsa Competizione Dedicated Server/server/cfg/settings.json', 'w') as outfile:
        json.dump(json_data, outfile, indent=4)
    
def create_event_json_file(track, pre_race_waiting_time_seconds, session_over_time_seconds,
                            ambient_temperature, cloud_level, rain, weather_randomness,
                            practice_hour_of_day, practice_day_of_weekend, practice_time_multiplier,
                            practice_session_duration, qualy_hour_of_day, qualy_day_of_weekend,
                            qualy_time_multiplier, qualy_session_duration, race_hour_of_day, 
                            race_day_of_weekend, race_time_multiplier, race_session_duration,
                            post_qualy_seconds, post_race_seconds):
    json_data = {
        "configVersion": 1,
        "track": track,
        "preRaceWaitingTimeSeconds": pre_race_waiting_time_seconds,
        "sessionOverTimeSeconds": session_over_time_seconds,
        "ambientTemp": ambient_temperature,
        "cloudLevel": cloud_level,
        "rain": rain,
        "weatherRandomness": weather_randomness,
        "sessions":
            [
                {
                "hourOfDay": practice_hour_of_day,
                "dayOfWeekend": practice_day_of_weekend,
                "timeMultiplier": practice_time_multiplier,
                "sessionType": "P",
                "sessionDurationMinutes": practice_session_duration
                },
                {
                "hourOfDay": qualy_hour_of_day,
                "dayOfWeekend": qualy_day_of_weekend,
                "timeMultiplier": qualy_time_multiplier,
                "sessionType": "Q",
                "sessionDurationMinutes": qualy_session_duration
                },
                {
                "hourOfDay": race_hour_of_day,
                "dayOfWeekend": race_day_of_weekend,
                "timeMultiplier": race_time_multiplier,
                "sessionType": "R",
                "sessionDurationMinutes": race_session_duration
                }
            ],
        "postQualySeconds": post_qualy_seconds,
        "postRaceSeconds": post_race_seconds,
        "simraceWeatherConditions": 0,
        "isFixedConditionQualifying": 0
    }
    with open('Assetto Corsa Competizione Dedicated Server/server/cfg/event.json', 'w') as outfile:
        json.dump(json_data, outfile, indent=4)

def create_event_rules_json_file(qualifying_stand_type, pit_window_length, driver_stint_time,
                                            mandatory_pitstop_count, max_total_driving_time, max_drivers_count,
                                            is_refuelling_allowed_in_race, is_refuelling_time_fixed,
                                            is_mandatory_pitstop_refuelling_required, is_mandatory_pitstop_tyre_changed_required,
                                            is_mandatory_pitstop_swap_driver_required, tyre_set_count):
    json_data = {
        "configVersion": 1,
        "qualifyStandingType": qualifying_stand_type,
        "pitWindowLengthSec": pit_window_length,
        "driverStintTimeSec": driver_stint_time,
        "mandatoryPitstopCount": mandatory_pitstop_count,
        "maxTotalDrivingTime": max_total_driving_time,
        "maxDriversCount": max_drivers_count,
        "isRefuellingAllowedInRace": is_refuelling_allowed_in_race,
        "isRefuellingTimeFixed": is_refuelling_time_fixed,
        "isMandatoryPitstopRefuellingRequired": is_mandatory_pitstop_refuelling_required,
        "isMandatoryPitstopTyreChangeRequired": is_mandatory_pitstop_tyre_changed_required,
        "isMandatoryPitstopSwapDriverRequired": is_mandatory_pitstop_swap_driver_required,
        "tyreSetCount": tyre_set_count
    }
    with open('Assetto Corsa Competizione Dedicated Server/server/cfg/eventRules.json', 'w') as outfile:
        json.dump(json_data, outfile, indent=4)

def create_assist_rules_json_file(stability_control_level_max, disable_autosteer,
                                                disable_auto_lights, disable_auto_wiper, disable_auto_engine_start,
                                                disable_auto_pit_limiter, disable_auto_gear, disable_auto_clutch,
                                                disable_ideal_line):
    disable_autosteer = int(disable_autosteer == True)
    disable_auto_lights = int(disable_auto_lights == True)
    disable_auto_wiper = int(disable_auto_wiper == True)
    disable_auto_engine_start = int(disable_auto_engine_start == True)
    disable_auto_pit_limiter = int(disable_auto_pit_limiter == True)
    disable_auto_gear = int(disable_auto_gear == True)
    disable_auto_clutch = int(disable_auto_clutch == True)
    disable_ideal_line = int(disable_ideal_line == True)
    json_data = {
        "configVersion": 1,
        "stabilityControlLevelMax": stability_control_level_max,
        "disableAutosteer": disable_autosteer,
        "disableAutoLights": disable_auto_lights,
        "disableAutoWiper": disable_auto_wiper,
        "disableAutoEngineStart": disable_auto_engine_start,
        "disableAutoPitLimiter": disable_auto_pit_limiter,
        "disableAutoGear": disable_auto_gear,
        "disableAutoClutch": disable_auto_clutch,
        "disableIdealLine": disable_ideal_line
    }
    with open('Assetto Corsa Competizione Dedicated Server/server/cfg/assistRules.json', 'w') as outfile:
        json.dump(json_data, outfile, indent=4)

def create_entry_list_json_file(registrations):
    json_data = {"configVersion": 1, "forceEntryList": 1}
    entry_drivers = []
    for registration in registrations:
        entry_drivers.append({
                    "drivers": [
                        {
                            "firstName": registration.user_br.first_name,
                            "lastName": registration.user_br.second_name,
                            "shortName": registration.user_br.short_name,
                            "driverCategory": 2,
                            "playerID": "S" + str(registration.user_br.steam_id)
                        }
                    ],
                    "raceNumber": -1,
                    "forcedCarModel": -1,
                    "overrideDriverInfo": 1,
                    "isServerAdmin": 0,
                })
    json_data["entries"] = entry_drivers
    with open('Assetto Corsa Competizione Dedicated Server/server/cfg/entryList.json', 'w') as outfile:
        json.dump(json_data, outfile, indent=4)